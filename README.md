# HeadFoundry

独立、clean-room 的多视角可编辑头模重建研究。**目前没有通过实际视觉验收的头模。**
技术测试通过不代表三维误差、完整头部或相似度达标。

## 当前状态

[0251](docs/experiment-0251-direct-photometric-pose-capacity.md) 的直接光度相机
能力检查也未通过：已知扫描几何下4/5投影误差低于3像素，但一个视角仍为
6.14像素，且光照拟合出现非物理负值。已停止并清理专用实现，保留精简证据。
这不是新重建头模，也未进入真人头模拟合。

0249 的图像初始化方案在已知三维验证中失败，未转入真人重建。
2026-10-20 按用户要求完成失败路线清理；旧实验说明保留为历史记录，
其中的专用脚本和大文件不保证仍在工作区。详见
[清理范围与恢复边界](docs/cleanup-0250-failed-routes.md)。

**以后先关闭并清理失败路线，再开始下一条路线。**规则写入 [AGENTS.md](AGENTS.md)。
不再把失败产物和其专用集成堆在活动代码中，也不降低门禁换取通过。

## 保留的研发基座

- `src/headfoundry`：输入授权、相机、扫描、通用数值几何及质量门禁。
- `tests`：共享功能、安全回归和成功的评估夹具；不是历次失败路线的测试集合。
- `tools`：授权资料接入、FLAME/CC0 资产准备、Blender 白模渲染、扫描评估。
- `assets/private`：本地授权资料、许可资产、成功评估基准；不提交到 Git。
- `docs`：原始需求、研究依据、实验结论与失败原因；历史源代码可从 Git 查找。

保留的通用几何代码并不构成已经成功的产品重建流水线。旧模型专用
运行入口、下载权重和失败候选已经退役；不要照历史文档自动重新安装。

## 开发与检查

基础依赖为 NumPy；需要几何求解时安装已有的 SciPy 可选组：

```powershell
python -m pip install -e ".[geometry]"
python -m unittest discover -s tests
python -m headfoundry.quality examples/quality_manifest.json
```

图像接入和渲染工具按需使用 Pillow/OpenCV/MediaPipe/Blender，不新增服务端或 UI。

## 依据与边界

- [需求与研究记录](docs/report-source.md)
- [质量优先决策](docs/adr/0001-quality-first-reconstruction.md)
- [来源及权利台账](docs/claim-source-ledger.md)
- [初始相机门禁](docs/experiment-0001-camera-baseline.md)

两例真实资料仅用于本地重建和误差验证，不上传、不训练。case001 开发，
case002 方案冻结后再验证。五张逐张生成的 AI 图不是严格多视角真值。
不使用 Peek 实现、KeenTools 私有服务或输出，不声称达到同等质量。
