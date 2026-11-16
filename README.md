# MIC 官网页面方案

为同济大学多媒体与智能计算实验室制作的四个独立、响应式前端方案，重点呈现研究方向和教师介绍。它们是设计预览，并非现有官网的已部署版本。

## 本地预览

无需安装依赖，在仓库根目录运行：

```sh
python3 -m http.server 8000 --directory dist
```

浏览器打开 <http://localhost:8000/>。方案 01、02、03、04 分别对应 `a.html`、`b.html`、`c.html`、`d.html`。方案 01 和 03 的研究条目可展开；方案 02 的方向索引可切换；方案 04 的研究主题可通过按钮切换，图片位置为文字说明的空白框。每个方案都提供教师资料来源链接。

教师照片直接引用 MIC 原站的公开图片地址，网络不可用时显示姓名首字母占位。其余页面无需外部依赖。

## 内容依据与范围

- [MIC 主页](https://mic.tongji.edu.cn/main.htm)：四个研究方向名称。
- [研究方向](https://mic.tongji.edu.cn/yjfx/list.htm)：研究条目及简述。子项的四类分组是为了演示页面结构而整理，并非官网已明确发布的分类。
- [教师介绍](https://mic.tongji.edu.cn/js/list.htm)：姓名、职称、研究领域和照片。更多资料分别链接至[王瀚漓教师资料](https://mic.tongji.edu.cn/gdxx/list.htm)与[倪张凯个人主页](https://eezkni.github.io/)。
- 参考 [CVLab 研究页](https://cvlab.unibo.it/research/)、[CVLab 团队页](https://cvlab.unibo.it/team/)、[UT Austin 计算机视觉研究页](https://www.cs.utexas.edu/research/computer-vision)和[伊利诺伊大学视觉与机器人实验室人员页](https://vision.ai.illinois.edu/people/)。

资料核对日期：2026-11-16。设计未虚构教师履历、论文或研究成果；上线使用前仍需由课题组复核内容与图片使用授权。
