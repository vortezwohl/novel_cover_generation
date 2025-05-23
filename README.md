## 书封生成 API

- 请求

    ```json
    {
        "task_type": "simple, 目前仅支持 simple 模式",
        "novel": "输入小说原文（用于生成封面的背景内容依据）, str",
        "title": "需要展示在封面上的标题文本, str",
        "title_height_correction": "[Optional] 标题在封面中的垂直位置修正值（用于调整标题上下偏移量）, float, 默认值: 0.0",
        "title_color": "[Optional] 标题文字颜色值（支持RGB列表形式，如[255,255,255]）, list, 默认值: None",
        "resample": "[Optional] 封面图片重采样次数, int, 默认值: 4"
    }
    ```
  
> `title_height_correction`, `title_color`, `resample` 可不给, 当 `title_color` 为空时, 默认使用聚类算法计算主题色, 使用主题色作为书名色.

- 响应

    ```json
    {
        "b64_images": ["base64编码的封面图片1", "base64编码的封面图片2", ..., "base64编码的封面图片n"]
    }
    ```
