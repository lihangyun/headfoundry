import unittest
import numpy as np
from headfoundry.epipolar import fundamental, sampson_distance, calibrated_pose, refine_pose, robust_refine_pose


class EpipolarTests(unittest.TestCase):
    def test_independent_points_and_corrupted_validation(self):
        rng=np.random.default_rng(42)
        points=rng.uniform(-1,1,(50,3));points[:,2]+=5
        first=points[:,:2]/points[:,2:]*900+500
        moved=points+np.array([.8,.1,0])
        second=moved[:,:2]/moved[:,2:]*900+500
        f=fundamental(first[:35],second[:35])
        self.assertLess(sampson_distance(f,first[35:],second[35:]).max(),1e-8)
        wrong=second[35:]+np.array([0,50])
        self.assertGreater(sampson_distance(f,first[35:],wrong).min(),30)
        self.assertEqual(np.linalg.matrix_rank(f),2)
        with self.assertRaises(ValueError):fundamental(first[:7],second[:7])
        with self.assertRaises(ValueError):fundamental(np.zeros((10,2)),np.zeros((10,2)))

    def test_calibrated_pose_recovers_rotation_and_translation_direction(self):
        rng=np.random.default_rng(7)
        points=rng.uniform(-1,1,(80,3));points[:,2]+=5
        angle=.3
        r=np.array([[np.cos(angle),0,np.sin(angle)],[0,1,0],[-np.sin(angle),0,np.cos(angle)]])
        t=np.array([.8,.1,.05]);other=points@r.T+t
        k=np.array([[900.,0,500],[0,900,500],[0,0,1]])
        a=points[:,:2]/points[:,2:]*900+500
        b=other[:,:2]/other[:,2:]*900+500
        result=calibrated_pose(a,b,k,k);e=np.array(result['extrinsic'])
        np.testing.assert_allclose(e[:,:3],r,atol=1e-8)
        np.testing.assert_allclose(e[:,3],t/np.linalg.norm(t),atol=1e-8)
        self.assertEqual(result['positive_depth_fraction'],1.)
        self.assertEqual(result['status'],'UNVERIFIED')
        # Training observations alone determine the refinement; the rest are unseen.
        refined=refine_pose(a[:60],b[:60],k,k)
        refined_e=np.array(refined['extrinsic'])
        np.testing.assert_allclose(refined_e[:,:3],r,atol=1e-8)
        np.testing.assert_allclose(refined_e[:,3],t/np.linalg.norm(t),atol=1e-8)
        self.assertLess(sampson_distance(refined['fundamental'],a[60:],b[60:]).max(),1e-8)
        self.assertEqual(refined['status'],'UNVERIFIED')
        noisy=b[:60]+rng.normal(0,.7,(60,2))
        linear=calibrated_pose(a[:60],noisy,k,k)
        linear_e=np.array(linear['extrinsic']);tx,ty,tz=linear_e[:,3]
        skew=np.array([[0,-tz,ty],[tz,0,-tx],[-ty,tx,0]])
        linear_f=np.linalg.inv(k).T@skew@linear_e[:,:3]@np.linalg.inv(k)
        fitted=refine_pose(a[:60],noisy,k,k)
        before=sampson_distance(linear_f,a[:60],noisy)
        after=sampson_distance(fitted['fundamental'],a[:60],noisy)
        self.assertLess(np.sum(np.sqrt(1+(after/2)**2)),np.sum(np.sqrt(1+(before/2)**2)))
        self.assertGreaterEqual(fitted['positive_depth_fraction'],.95)

    def test_robust_training_consensus_recovers_noisy_outlier_pairs(self):
        from scipy.spatial.transform import Rotation
        rng=np.random.default_rng(37)
        points=rng.uniform(-1,1,(140,3));points[:,2]+=5
        r=Rotation.from_rotvec([.03,.3,-.01]).as_matrix();t=np.array([.8,.1,.05])
        other=points@r.T+t;k=np.array([[900.,0,500],[0,900,500],[0,0,1]])
        a=points[:,:2]/points[:,2:]*900+500;b=other[:,:2]/other[:,2:]*900+500
        for bad in (10,20):
            with self.subTest(wrong_pairs=bad):
                noisy=b[:100]+np.random.default_rng(23).normal(0,.3,(100,2))
                noisy[:bad]=b[np.random.default_rng(24).permutation(100)[:bad]]
                result=robust_refine_pose(a[:100],noisy,k,k)
                e=np.asarray(result['extrinsic'])
                self.assertLess(np.degrees(Rotation.from_matrix(e[:,:3]@r.T).magnitude()),.5)
                self.assertLess(np.degrees(np.arccos(np.clip(e[:,3]@t/np.linalg.norm(t),-1,1))),2.)
                unseen=sampson_distance(result['fundamental'],a[100:],b[100:])
                self.assertLess(np.percentile(unseen,95),.5)
                self.assertGreater(np.percentile(sampson_distance(result['fundamental'],a[100:],b[100:]+[0,30]),95),10)
                self.assertEqual(result['candidate_count'],100)
                self.assertGreaterEqual(result['support_fraction'],.75)
                self.assertGreater(result['candidate_sampson_p95_px'],10)
                self.assertGreaterEqual(result['positive_depth_fraction'],.95)
                self.assertGreaterEqual(result['parallax_median_deg'],1.)
                self.assertLessEqual(result['parallax_p05_deg'],result['parallax_median_deg'])
                self.assertGreaterEqual(result['parallax_p95_deg'],result['parallax_median_deg'])
                self.assertEqual(result['status'],'UNVERIFIED')
                repeated=robust_refine_pose(a[:100],noisy,k,k)
                np.testing.assert_array_equal(result['fit_inlier_indices'],repeated['fit_inlier_indices'])
                np.testing.assert_array_equal(result['extrinsic'],repeated['extrinsic'])

    def test_robust_pose_rejects_unsupported_and_degenerate_inputs(self):
        rng=np.random.default_rng(45);k=np.array([[900.,0,500],[0,900,500],[0,0,1]])
        a=rng.uniform(100,900,(50,2));b=rng.uniform(100,900,(50,2))
        with self.assertRaises(ValueError):robust_refine_pose(a,b,k,k,iterations=64)
        with self.assertRaises(ValueError):robust_refine_pose(a[:11],b[:11],k,k)
        with self.assertRaises(ValueError):robust_refine_pose(np.zeros((20,2)),np.zeros((20,2)),k,k)
        with self.assertRaises(ValueError):robust_refine_pose(a,a+[60,10],k,k,iterations=16)
        with self.assertRaises(ValueError):robust_refine_pose(a,b,k,k,threshold_px=float('nan'))
        with self.assertRaises(ValueError):robust_refine_pose(a,b,k,k,iterations=False)
        with self.assertRaises(ValueError):robust_refine_pose(a,b,k,k,min_support_fraction=0)
        with self.assertRaises(ValueError):robust_refine_pose(a,b,k,k,min_parallax_deg=0)
        duplicated=a.copy();duplicated[0]=duplicated[1]
        with self.assertRaisesRegex(ValueError,'duplicate'):robust_refine_pose(duplicated,b,k,k)
        with self.assertRaisesRegex(ValueError,'duplicate'):robust_refine_pose(b,duplicated,k,k)
        invalid_k=k.copy();invalid_k[1,0]=200
        with self.assertRaisesRegex(ValueError,'intrinsics'):robust_refine_pose(a,b,invalid_k,k)

    def test_robust_pose_rejects_noisy_pure_rotation(self):
        from scipy.spatial.transform import Rotation
        points=np.random.default_rng(0).uniform(-1,1,(100,3));points[:,2]+=5
        r=Rotation.from_rotvec([.03,.3,-.01]).as_matrix();other=points@r.T
        k=np.array([[900.,0,500],[0,900,500],[0,0,1]])
        a=points[:,:2]/points[:,2:]*900+500
        b=other[:,:2]/other[:,2:]*900+500+np.random.default_rng(23).normal(0,.3,(100,2))
        # Before the guard, this returns 100% positive depths and 0.412 px
        # training p95 despite the true baseline being zero (depth is unobservable).
        with self.assertRaisesRegex(ValueError,'insufficient triangulation parallax'):
            robust_refine_pose(a,b,k,k)
