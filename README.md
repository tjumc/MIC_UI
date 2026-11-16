# MIC 官网设计与前端代码

同济大学多媒体与智能计算实验室的完整静态网站方案，包含首页、研究方向、团队（教师、成员、校友）、学术论文、课程信息、动态和联系我们，并提供中英页面。五个研究方向及杜杉杉、吴秀哲的教师名单依据用户要求；两位老师的职称与简介按要求留空。

## 方案浏览

在 `dist/concepts/index.html` 可比较三套完整方案：原有简洁学术版、期刊索引版和信息门户版。两套新增方案各包含完整中英文栏目；信息门户版可在浏览器本地收藏论文。原有四个设计概念仍在 `dist/archive/`。

## 本地预览

无需安装依赖，打开 `dist/index.html` 即可，也可以在仓库根目录运行：

```sh
python3 -m http.server 8000 --directory dist
```

访问 `http://localhost:8000/`。原来四个方案完整保存在 `dist/archive/`，可打开 `dist/archive/index.html` 查看。旧入口 `d.html` 会转到新首页。

## 维护

- 页面结构和中英文案在 `src/build.py` 中；运行 `python3 src/build.py` 重新生成原方案。两套新增方案由 `python3 src/build_variants.py` 生成。
- 共用样式与交互在 `dist/site.css` 和 `dist/site.js`，新增方案各自的样式与交互位于 `dist/concepts/`。名单、论文、课程数据共用 `dist/data/`。
- 所有新站图片位置均为空白说明框，不含占位照片。
- 成员和校友记录整理于 2026 年 11 月；校友去向是历史记录，可能已发生变化。课程为 2011–2021 年历史记录，不代表当前开课安排。
- 论文列表依据原站公开记录整理，包含原站列出的 232 条记录；正式使用前请课题组复核内容和更新状态。

## 资料来源

内容依据 [MIC 成员](https://mic.tongji.edu.cn/cy/list.htm)、[校友](https://mic.tongji.edu.cn/xy/list.htm)、[论文](https://mic.tongji.edu.cn/xslw/list.htm)、[课程](https://mic.tongji.edu.cn/kcxx/list.htm)、[联系](https://mic.tongji.edu.cn/lxwm/list.htm)和[教师介绍](https://mic.tongji.edu.cn/js/list.htm)页面，以及用户提供的最新研究方向和教师名单。页面布局参考 [CVLab](https://cvlab.unibo.it/)，没有使用其品牌或图片素材。
