# HeadFoundry：同类产品、公开技术路线与重选方案

核查日期：2026-10-14。状态：**研究报告与实施建议，非产品质量验收，也不是内部算法复现证明**。

本轮按用户要求，由三个子agent分别研究产品、技术证据和免费商业可行性；主agent
交叉核对关键来源、现有失败记录及逆向边界。范围是可编辑人头**外表面**，不是CT颅骨。
只读公开资料与HeadFoundry已有记录：没有运行竞品、调用私有API、下载新权重、上传
参考图、读取Peek实现、改变重建代码或提升任何默认头模。

## 1. 结论先行

1. **同类产品确实存在，但不能按宣传图宣布“与KeenTools同级”。** 本轮没有同输入、
   同相机、同灯光白模的实测，所有直接质量排名都仍是`UNVERIFIED`。
2. **不用私有逆向，公开资料已经能揭示重要架构。** FaceBuilder披露统计头模、相机、
   跨视图pins和局部形变；公开会议演讲进一步提到局部patch的参数化模型、神经网络与
   constrained bundle adjustment。它不是“必须先找到一个神秘端到端大模型”。
3. **我们当前实现失败，不证明整个统计拟合范式错误。** 真正需要区分的是形状表达上限、
   观测/对应质量和相机，而非再换求解器或增加同一loss的权重。
4. **还没有找到已经验证质量、整条依赖链清楚、下载即可使用的免费商业替代品。**
   这只是本轮检索结论，不是对所有现存或未来模型的不存在证明。
5. **近期优先研究“全局先验＋有解剖约束的多尺度局部残差”，先用可靠监督验证表达能力。**
   中期再解决稠密观测/自动化。若接受更严格采集条件，真实几何测量＋自研拓扑注册是
   不必先训练的另一条独立路线。两条都不是已经取得成功的新算法。

## 2. 产品矩阵：把照片建模、扫描和拓扑整理分开

以下是公开功能/方法，不是实测质量排名；收费产品仅作研究参照，不建议采购并嵌入。

| 产品/系统 | 输入与实际交互 | 可核实的路线/产物 | 对HeadFoundry的价值与限制 |
|---|---|---|---|
| **KeenTools FaceBuilder** | 少量多角度照片；跨视图pin拖动，支持自动初对齐后人工修正 | 统计模型、相机估计、局部影响的形变；可导出清洁拓扑头模。Nuke FAQ明确pins/相机用于形状求解 | 最接近交互照片建模参照；内部模型、目标函数和训练集未完整公开。不能把它与Cloud自动管线完全等同。[官方Nuke页](https://keentools.io/products/facebuilder-for-nuke)、[Blender页](https://keentools.io/products/facebuilder-for-blender) |
| **Headshot 3 / Character Creator 5** | 正面图初始化；90°侧面参考、对齐、控制点及视口修形，也支持网格流程 | 输出可编辑CC头部/角色；官方手册明确展示侧面深度修正及拓扑对比 | 当前已是3代，不能只调研2代。说明“人工修形＋多视角参照”是正式产品能力，不是自动模型失败后隐藏的步骤。私有收费，不引入其生成服务。[产品](https://www.reallusion.com/character-creator/headshot/)、[侧面手册](https://manual.reallusion.com/Headshot_Plugin/ENU/3.0/04-Image-Mode/Refining-Side-Face.htm) |
| **FaceGen Modeller / PhotoFit SDK** | 正面/侧面照片、特征点、参数调整 | 公开PCA统计先验：273张高分辨率3D扫描；50维对称形状、30维非对称形状、50维颜色。输出网格及morph | 是“统计先验＋照片拟合”的明确商业实例。官方也承认控制项相关，未公开完整方法论文；多几个PCA维度不是有证据的解药。SDK和分发另有许可。[FAQ](https://facegen.com/faq.htm)、[PhotoFit](https://facegen.com/man_create_photo.htm)、[产品](https://facegen.com/modeller.htm) |
| **Avatar SDK / MetaPerson** | 单张selfie自动生成，编辑器或API | 输出rigged GLB/glTF/FBX等真实网格，内部重建私有 | 可研究自动化接口与身份可辨识目标。团队白皮书的正面有纹理渲染识别距离，不能证明白模双侧几何准确；本地计算也不自动等于完全离线或免费嵌入。[API](https://avatarsdk.com/avatar-api/)、[FAQ](https://avatarsdk.com/faq/)、[白皮书](https://docs.avatarsdk.com/pub/White_paper_-_Avatars_you_can_recognize.pdf) |
| **Mesh to MetaHuman / MetaHuman Creator** | 已有扫描、雕刻或网格；Identity conform/markers等流程 | 官方5.0–5.5文档披露：模板贴合输入体积→数据库近似→rig配置→保留真实体积与近似的最终形状delta | 重要启发是“不强迫个体完全落入低维数据库”。但它需要已有几何，不等于从随意五图凭空恢复；免费门槛不等于开源/可嵌入自家重建服务。[当前流程](https://dev.epicgames.com/documentation/en-us/metahuman/from-mesh)、[版本限定的技术解释](https://dev.epicgames.com/documentation/en-us/metahuman/metahuman-identity-asset?application_version=5.0-5.5)、[许可](https://www.metahuman.com/license?lang=en-US) |
| **Faceform Wrap（原R3DS系列）** | 真实扫描/雕刻＋基模＋可选对应点 | 由粗到细、密度增加的控制节点非刚性配准，输出统一拓扑 | 解决“把已测几何变成生产网格”，不是照片深度恢复。公开算法说明很有参考价值，软件/输出的竞争性使用受EULA限制。[方法手册](https://docs.faceform.com/Wrap/Nodes/Wrapping/Wrapping.html)、[EULA](https://docs.faceform.com/Wrap/LicenseAgreements/Wrap/WrapEULA.html) |
| **Wrap4D / ImageFacialWrapping** | 已标定双相机、初始几何、个体化reference blendshapes及纹理 | 几何与图像/深度拟合、光照模拟、多分辨率和可见性/不确定性处理 | 值得研究工程分层，但其个体先验是前置成本，不能作为现成通用五图初始化器。[节点手册](https://www.faceform.com/docs/Wrap/Nodes/ImageFacialWrapping/ImageFacialWrapping.html) |
| **Clear Angle Studios TopoTrack / DI4D技术** | 专业中性扫描、FACS/4D与多相机数据，另有HMC生产流程 | 同拓扑/UV的高密度跟踪，个体表情数据与人工QC | 高保真背后有强采集与人工检查。DI4D技术现已进入CAS，不能当作仍独立销售的普通免费软件。[迁移声明](https://www.clearanglestudios.co.uk/di4d/)、[TopoTrack](https://www.clearanglestudios.co.uk/topotrack/) |
| **3dMDface / trio / head** | 同步多视角主动立体摄影测量；不同配置覆盖不同范围 | 直接测量三维几何并输出纹理网格/点云 | 高质量采集参照，不是同输入照片算法。厂商设备精度不能变成任意照片拟合精度；本轮未完成其独立精度论文全文复核。[产品](https://3dmd.com/products/) |
| **Artec扫描＋Studio** | 手持硬件采集，跨帧/全局注册与融合 | 真实扫描网格及常见格式导出 | 说明测量、注册、融合的分工；人脸运动/反光仍有困难。商业硬件/软件，不是本项目免费核心。[人脸扫描](https://www.artec3d.com/learning-center/best-3d-face-scanner)、[处理流程](https://docs.artec3d.com/as/16/en/process.html) |
| **Metashape / RealityScan Desktop** | 同一真实对象、高重叠照片或多相机采集 | 通用SfM/MVS、网格与纹理 | 可以提供真实几何来源，不解决独立AI图的不一致。Metashape收费；RealityScan免费有收入等条件，不等于开源或可转授权。[Metashape](https://www.agisoft.com/features/professional-edition/)、[RealityScan许可](https://www.realityscan.com/license) |

3Lateral/Rig Logic不另算一个同输入照片重建产品：公开白皮书主要解释运行时rig映射，
不是照片到形状的完整逆过程。[Rig Logic资料](https://www.metahuman.com/learning/the-tech-behind-metahuman-creator-face-rigs?lang=en-US)

## 3. 不用私有逆向，已经能确认哪些关键技术

### 3.1 KeenTools：有公开架构，没有内部公式

**已披露事实：**

- FaceBuilder Nuke产品页说明，相机设置与pins约束统计模型形状；参考图不是直接的
  三维扫描。这个说明只约束该产品的公开描述，不能据此排除Cloud使用图像网络。
- 2022.2官方更新明确描述pin的影响更局部，并举嘴角、弯曲鼻形和皮肤折痕为例。
- 3DBODY.TECH 2024会议原页提供KeenTools负责人演讲。主办方发布的公开片段转录中，
  演讲者明确提到带局部patch的参数化3D morphable model、神经网络和受约束的bundle
  adjustment。转录有明显识别错误，只支持这些高层要素；没有取得其内部实现。

来源：[Nuke官方说明](https://keentools.io/products/facebuilder-for-nuke)、
[2022.2更新](https://keentools.io/news/2022-2)、
[会议原页](https://proc.3dbody.tech/abstracts/2024/2470.html)、
[主办方公开视频转录](https://www.linkedin.com/posts/nicola-dapuzzo-phd_3dbodytech-conference-expo-2024-flashback-activity-7309260721807147009-36L6)。

演讲者还提出过精度数值，但本轮没有该基准的对象数、误差定义、标定、扫描真值和
原始结果，**不采用为可复现精度承诺**。2024演讲也不是2026内部实现的完整规格。

**合理推断，而非确认的内部机密：**

KeenTools优势可能来自局部表达能力、可靠对应/交互约束、相机与形状的正确联合、
训练数据及长期工程积累。公开信息不支持断言“它就是某个公开模型＋某求解器”。
尤其不能因为GitHub公开组织中有某求解器fork，就认定产品一定用了它、或它造成质量差距。

### 3.2 生产级的共同点：保留测量形状，而不是只挑一个近似模板

MetaHuman上述版本的文档明确保留输入体积相对数据库近似的delta，同时警告大delta
会影响眼嘴等区域的动画稳定性。这不是无限自由拉点，而是基础结构与个体残差分开。
Wrap则公开了从粗到细的控制节点、对应点和不参与拟合区。两者启发独立的设计选择，
不能照搬私有节点或认为照着公开流程就获得了它们的数据和质量。

对本项目的推论是：低维prior可以负责初始化/合理性，不能未经能力验证就充当最终
身份的硬上限；局部自由度须作用于连续3D表面，并明确接触、唇体及周边皮肤约束。
这与已拒绝的“把donor图像深度贴进嘴区”不是同一表示。

## 4. 研究方法与可商用组件：不能只看仓库顶层license

| 研究/组件 | 公开技术线索 | 当前采用判断 |
|---|---|---|
| **COLMAP / PyCOLMAP 4.2.0** | SfM/BA→深度/法线→融合→表面；不需要训练人脸网络 | 本体BSD，项目已有精确锁。实际依赖/构建另审。Windows普通wheel不能当作现成CUDA密集链；官方说明PatchMatch需CUDA编译。[教程](https://colmap.github.io/tutorial.html)、[4.2.0](https://pypi.org/project/pycolmap/4.2.0/) |
| **Disney被动立体人脸采集** | 标定/同步多相机、被动stereo与人脸细化，论文含几何验证 | 证明更强观测可以改变质量上限，不是五张任意图替代算法；方法/代码/专利分别审。[原研究](https://la.disneyresearch.com/publication/high-quality-single-shot-capture-of-facial-geometry/) |
| **USC偏振球面梯度/Light Stage** | 受控光照、分离反射、法线与多视角几何 | 高质量参考，硬件/采集成本高。存在公开专利线索，论文可读不等于自由实施已清除。[研究](https://vgl.ict.usc.edu/Research/Multiview/)、[专利线索](https://patents.google.com/patent/US20120268571A1/en) |
| **HRN/MV-HRN** | 粗模型＋中频形变＋高频细节及多视角一致性 | 层次表达有参考价值；不是没研究过的全新捷径，细节丰富不等于鼻唇颏身份正确。精确权重仍需单独审核。[官方](https://github.com/youngLBW/HRN) |
| **Pixel3DMM** | DINO特征→dense UV/normal→几何拟合 | 代码/发布权重NC，不能直接进入商业链；公开方法可作独立研究对象。不能使用受限教师输出规避权重限制。[项目](https://simongiebenhain.github.io/pixel3dmm/)、[官方仓库](https://github.com/SimonGiebenhain/pixel3dmm) |
| **VGGTFace / UVFaceFusion** | 多视图点图与canonical UV融合；UVFaceFusion为后续工作 | 顶层分别MIT/GPLv3，不覆盖Pixel3DMM UV与VGGT依赖。GPL本身不禁止商用，关键是整链权利/义务。UVFaceFusion已有base-resolution推理，详细推理/训练仍列TODO，不得说完全未开源。[VGGTFace](https://github.com/grignarder/vggtface)、[UVFaceFusion](https://github.com/grignarder/UVFaceFusion) |
| **RealDenseFace（2026）** | dense UV对应＋relative depth→逐顶点目标→CUDA Gauss–Newton拟合；有单图、序列及多视图示例 | **当前代码MIT已核实**；不能沿用初稿“无LICENSE”判断。checkpoint、face_box.pth、flame_assets.npz、FLAME版本和上游权利仍须分项核对；不是已批准的新资产。[官方](https://github.com/LinzhouLi/RealDenseFace)、[LICENSE](https://github.com/LinzhouLi/RealDenseFace/blob/main/LICENSE)、[论文](https://arxiv.org/abs/2608.09238) |
| **FlowFace** | 从高质量scan标注学习dense UV-to-image对应，迭代跟踪 | 证明升级观测是有研究支持的方向；不能因论文存在承诺开箱运行和免费商业权重。[论文](https://openaccess.thecvf.com/content/CVPR2024/papers/Taubner_3D_Face_Tracking_from_2D_Video_through_Iterative_Dense_UV_CVPR_2024_paper.pdf)、[仓库](https://github.com/felixtaubner/flowface/) |
| **MonoNPHM** | nonlinear SDF头部先验＋canonical形变/纹理，逐序列拟合 | 代码MIT明确**不包含数据和预训练模型**；需要强先验与拓扑整理，不是直接免费替换。[方法](https://simongiebenhain.github.io/MonoNPHM/)、[许可原文](https://raw.githubusercontent.com/SimonGiebenhain/MonoNPHM/main/LICENSE) |
| **NeuFace** | 形状先验＋额外位移、BRDF和环境光联合逆渲染 | 有助理解形状/反射歧义；代码许可不解决ImFace、FaceScape或权重链，不能直接集成全链。[论文](https://arxiv.org/html/2303.14092v1)、[代码](https://github.com/aejion/neuface) |
| **普通DINOv2 S/B/L/g** | 通用图像特征；含register版本，patch size 14 | 官方模型卡Apache-2.0；可以成为候选backbone，但不是精确脸部UV/深度预测器。本轮未下载或批准新hash。[模型卡](https://github.com/facebookresearch/dinov2/blob/main/MODEL_CARD.md) |

### RealDenseFace专项审计：值得关注，但不急于安装

它确实改变“只有稀疏点/轮廓”的观测形式，因此比再换一个泛用3D生成器更值得关注。
但源代码MIT不能简单外推到Google Drive发布checkpoint或第三方资产。

专项复核源码版本为 `ebf0063835f520f07fdf5a813b1af9cdc0ae46b5`。Drive包内容本轮
未读取，不能声称包内没有许可证；准确结论是尚未取得明确覆盖checkpoint的授权证据。
`face_box.pth`检测器和`flame_assets.npz`的UV/可见性数据需独立追溯。未知不等于禁止，
也不等于可直接采用。论文提及MICA不证明发布代码一定有相同运行依赖。

复核当前公开版本，还需追踪DINOv3模型/条款、face_box及FLAME附属资产来源；
requirements还包含本项目当前排除的nvdiffrast。`pretrained=false`只可能阻止另行
下载，不会自动消除已训练checkpoint的上游权利。DINOv3不是简单的NC标签，仍应
逐条检查其自定义许可。[DINOv3许可](https://github.com/facebookresearch/dinov3/blob/main/LICENSE.md)

论文使用的训练/注册资料与MICA等先验，也应与源码许可分开核查。尚未澄清的权利
意味着fail closed，**不等于已证明模型必然禁止一切商业使用**。未取得授权前不下载
不明权重、不将其输出作为商业训练标签。现成standard FLAME与本项目精确FLAME
2023 Open的语义/版本兼容性同样需要证明，不能只改文件名。

适配还涉及表情空间、关节/蒙皮、pose corrective与UV，项目已有的中性身份解码
不涵盖这些契约。FLAME官方另列standard→Open的表情转换，进一步说明不能假设两者
参数可互换；转换器自身依赖也不因官方链接就自动获商业授权。
[官方发布页](https://flame.is.tue.mpg.de/)、
[官方模型许可](https://flame.is.tue.mpg.de/modellicense.html)。

## 5. “逆向工程”能不能帮忙：先拆成三种行为

以下是研究边界，不是针对具体法律争议的法务意见。

| 行为 | 本项目判断 | 可以取得的信息 |
|---|---|---|
| 阅读公开官方手册、论文、会议演讲、公开API/格式、专利公开文本；研究许可明确的独立组件 | **可以，本轮已执行** | 输入假设、分层架构、局部形变、几何/纹理分工、交互设计、已披露优化与评价方法 |
| 对合法取得的软件作标准功能观察、互操作或其他分析 | **不能一概说全部违法，也不能默认允许**；须先具体核对产品/版本、条款、目的、管辖、数据及用户授权；本轮未做 | 条款允许时可研究外部行为/互操作，不能凭观察唯一识别内部网络、损失或数据 |
| 使用受禁止的竞争性黑盒实验、破解/绕过许可或认证、提取私有底模/权重/参数、复制实现、用受限输出训练替代品 | **当前不做**；与既有clean-room边界或明确条款冲突 | 不纳入技术方案的证据来源，不以“买过/试用过”视为权限充分 |

当前核对的 **KeenTools Cloud API及桌面插件EULA（均标2026-08-20）第2.4条**，
明确限制逆向及使用软件/服务创建竞争产品；自定义书面协议可能另行约定。
Wrap也限制竞争/替代产品及逆向；Reallusion Content标准许可限制其Content及
Derivative Content的竞争用途、角色生成API和ML/AI训练。不能把内容条款泛化成
所有自有素材在所有场景的法律结论，但足以否定“随便用竞品输出做训练数据”的前提。

来源：[KeenTools API EULA](https://cloud.keentools.io/legal/terms-of-service)、
[插件EULA](https://link.keentools.io/eula)、
[Wrap EULA](https://docs.faceform.com/Wrap/LicenseAgreements/Wrap/WrapEULA.html)、
[Reallusion Content EULA](https://www.reallusion.com/Content/EULA/EULA.htm)。

不同地区对学习/观察、互操作与反编译有不同限定，不能把“逆向”一词整体当作
有或没有许可。例如中国条例区分软件思想原理研究，欧盟2009/24/EC第5/6条区分
观察测试与互操作反编译，美国17 USC1201(f)是有条件的互操作例外；都不是
“为了做竞争产品就可无条件提取”的通行证。本项目不自行用这些例外覆盖既有边界。
来源：[中国官方条例](https://www.cac.gov.cn/2013-02/08/c_12648744.htm)、
[欧盟官方文本](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A32009L0024)、
[美国官方文本](https://www.govinfo.gov/content/pkg/USCODE-2024-title17/html/USCODE-2024-title17-chap12-sec1201.htm)。

**公开专利也不等于免费许可。** 本轮只做来源定位，不是完整专利检索或自由实施
分析（FTO）；没有查到可核实的KeenTools专利号不证明其没有专利。公开论文的独立
实现仍需审查相关权利要求、地域、有效状态与适用范围。

## 6. 对既有失败的重新解释

已证实的事：

- 0205–0207提高了实际表面、可见性、导数与网格检查可靠性，但仍有通用鼻唇颏和
  视角间退化，尚无完整视觉通过。参见[交接](2026-10-14-project-handoff.md)。
- 0188–0193在已知共同3D的合成基准上也不稳定，所以不能把所有失败都归因于五张AI图。
- 0192的39个理想材料对应有收益；在**220×220图上**加入1px噪声会严重退化。
  这不是对1254px原图噪声的实际标定，也没有证明所有形状表达已经足够。
  [0192](experiment-0192-oracle-face-correspondence.md)、[0193](experiment-0193-noise-calibrated-head-prior.md)。

尚未证实的事：

- 当前30维GNM形状空间在直接高质量3D监督下，能否表达所需鼻唇颏形态。
- 形状表达不足、对应偏差、相机偏差各自对失败的贡献。
- 一种更自由但受控的局部表示是否会稳定改善，而非再次造成唇体折叠。

所以不能再把“都是统计模型”当等价，也不能认定继续当前拟合就会质变。
应停止的是已拒绝的具体表示/观测与无止境同类扫描；不是凭失败就否定所有先验拟合。

## 7. 候选产品与技术路线：近期优先级

### 路线A：照片参照＋全局先验＋局部残差（近期优先验证）

这是从FaceBuilder/Headshot的公开产品设计和MetaHuman残差机制推导的**自研候选**，
不是复制其内部实现，也不是已经证明质量的新方案。

`合法基模/粗身份 → 语义部位及可靠对应 → 多尺度连续3D局部残差 → 相机/表情分离 → 拓扑/接触/可见性约束 → 同场白模`

- 复用现有manifest、许可锁、投影、导出、可见性检查与Blender；不新建服务框架。
- 全局prior负责合理初值，局部表达负责超出低维先验的个体鼻、唇、颏形状；不是
  逐像素深度贴片，不是随意放开全部顶点，也不是只加更多同类PCA参数。
- 首轮使用真值监督或明确人工对应来验证表达能力，避免先把预测器错误混进来。
- 可允许人工修正以证明建模工具价值，但必须明示它是交互阶段；不能把它宣称为
  原始目标中的全自动照片重建。最终自动化还需要可靠的观测获取。
- 现有五张独立AI图只能对应“参考驱动的统一头部设计”；沿用正面主参考、两侧软约束，
  对冲突进行明确折中，不能宣称恢复唯一真实头骨或共同相机。
- **未解决核心风险：**没有证明这种局部表示在我们的合法基模上既足够表达又保持自然。

### 路线B：一致采集→真实几何→自研拓扑注册（无训练备选）

`同一真实/固定3D对象＋高重叠/可标定图 → SfM/BA → MVS → 置信几何 → 独立非刚性模板注册 → 固定拓扑`

- 可复用COLMAP/PyCOLMAP等已审基础，不采购Wrap/Metashape私有核心，不训练人脸网络。
- 决定性改变是“个体几何来自测量”，不是再拿五张独立图重跑0105。
- 必须承认皮肤低纹理、油光、微表情、顺序拍摄运动和同步/光照成本；5–10张普通
  图未必够。不允许悄悄把产品输入改成大型摄影棚还宣传原来的便利性。
- 若坚持只有现有五张独立AI图，此路线不能作为物理重建方案。

### 路线C：合法稠密对应预测＋canonical融合（自动化研发方向）

`许可明确的backbone → 自研或充分清权的dense UV/normal/relative-depth＋置信度 → 多视图几何约束 → 局部残差头模`

- 比当前稀疏观测有本质变化；RealDenseFace等可以成为研究对象，但尚未通过整链资产门禁。
- 若找不到清权可用的预测器，就必须自研/训练；不能把“不训练”与“仍要自动同级质量”
  当作已经兼容的承诺。普通DINOv2只是特征，不提供现成精确鼻唇对应。
- 自有3D合成监督需独立合法、足够多样的形状；若全来自同一有限prior，只会把其
  能力上限蒸馏得更快。训练/评价按身份分开，不能只换灯光视角。
- 本地8GB GPU的可训练规模、域差距、收敛与商业质量均需实测；本轮不给无依据工期。

## 8. 下一步应做的判别试验，而不是又一次盲拟合

下面是建议，**本轮没有执行**。按最小正确实现原则，先证明最关键的不确定性，
再决定是否安装预测器、训练网络或扩建生产线。

1. **表达能力上限：**直接给合法固定3D头的稠密表面/语义对应监督，冻结真相机，
   比较现有形状空间与一个有解剖保护的多尺度局部残差表示。排除图像检测与相机误差。
   这不同于0192的39点、同族受限方向实验；不能把旧测试换名重跑。
2. **观测上限：**只有表达上限过关，再用真值相机＋真值dense图像对应，逐步加入
   已声明误差/遮挡，看什么时候失败；然后才比较真实预测器或人工观测。
3. **输入域验证：**共同几何数据用于3D/相机验收；现有AI图只测试设计参考匹配。
   新真实采集或训练范围需要相应权利与同意，不沿用五图本地验证许可外推。
4. **可见交付：**每个候选必须有固定场景正面、两个斜侧、双纯侧白模，以及鼻—唇—
   下巴局部和独立3D误差。不能让纹理、漂亮单视角、平均数或测试数量替代验收。
5. **止损：**预先写主假设与判据；一次主试验，仅为已定位实现错误保留一次纠正重跑。
   没有明确白模与受保护视角进步，就冻结该候选，不失败后无限换权重/幅度/正则继续。

**建议决策：先验证A的表达上限；B保留为输入条件改变后的独立几何路线；C做清权与
观测研发，不直接承诺现成替代。** 这不修改原PRD最终目标、不放宽质量门禁，也不
把商业竞品的宣传或公开架构记作HeadFoundry的实施成果。

## 9. 本轮事实核查与交接

- 三个agent的分工是产品现状、公开技术、开源商业可行性；这是并行研究，不是三次
  独立实验或三方质量认证。
- 交叉核对修正两项初稿风险：RealDenseFace当前确有MIT代码许可；UVFaceFusion已有
  基础推理代码。二者都不能由此推导整链权利已清或质量已达标。
- 官方手册不同版本可能冲突，报告对Nuke、Blender、Cloud、UE版本分别限定，未将
  它们拼成虚构的内部设计说明。
- 仅生成本文；没有新模型安装、权重接入、账户协议接受、竞品运行、训练、重建、
  视觉验收或代码测试。旧失败产物和原有未提交0207记录均保留。
- 本轮专利工作是线索定位，非系统FTO；版权/合同适用性未作法律担保。

进一步落地应首先补本报告列明的未知项与资产清单，再提交独立实验方案。不得把
“公开能看到架构”误写为“已复刻KeenTools”，也不得再以大量工程迭代代替质量结果。
