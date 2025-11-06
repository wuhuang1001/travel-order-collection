# 项目简介

本项目用于获取某出行平台的详细信息 🤔

# 运行

运行环境：python3.8

1. 安装requirements.txt中的依赖

2. 运行main.py

```
python main.py
```

## 注意事项

需要注意，目前还未对多页数据进行处理，一次最多爬取50条数据，如果超出五十条数据，请运行`another_page.py`保存另外的数据


```
python another_page.py
```

*此为临时解决方案，如果数据量过大，请修改`another_page.py`中的`pagenum`参数，每页50条*


**本项目仅供学习交流使用，请勿用于商业用途。**