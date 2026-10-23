"""Independent floating pixel-score controls;no model,assets or file IO."""
import numpy as np

def oracle_controls(target):
    target=np.asarray(target,np.float64)
    if target.ndim!=2 or target.shape[1]!=2 or not len(target) or not np.isfinite(target).all():
        raise ValueError('finite nonempty paired pixel coordinates required')
    scorer=lambda uv:np.linalg.norm(uv-target,axis=1)
    wrong=scorer(target+[40,0]);roundoff_bound=8*np.finfo(np.float64).eps*max(1,float(abs(target).max())+40)
    wrong_error=float(abs(wrong-40).max())
    report={'zero_max_px':float(scorer(target).max()),'wrong40_max_roundoff_px':wrong_error,
        'roundoff_bound_px':roundoff_bound,'bound_basis':'8*float64 epsilon*max(1,max_abs_true_uv+40),not a physical threshold',
        'prediction_arrays_opened':False}
    if report['zero_max_px']!=0 or wrong_error>roundoff_bound or float(np.percentile(wrong,95))<=3:
        raise ValueError('independent scoring controls fail')
    return report

