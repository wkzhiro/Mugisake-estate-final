import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image

st.title('Streamlit 超入門')

st.write('DataFrame')

df = pd.DataFrame({
    '１列目': [1, 2, 3, 4],
    '２列目': [10, 20, 30, 40]
})

st.dataframe(df.style.highlight_max(axis=0), width=1000, height=200)

"""
# 章
## 節
### 項

```python
import streamlit as st
import numpy as np
import pandas as pd
```

"""

df = pd.DataFrame(
    np.random.rand(20,3),
    columns=['a', 'b', 'c']
)

st.line_chart(df)


df = pd.DataFrame(
    np.random.rand(100,2)/[50, 50] + [35.69, 139.70],
    columns=['lat', 'lon']
)

st.map(df)

# Image.open('sample.jpeg')
# st.image(img, caption='Kazushi', use_column_width=True)

option = st.selectbox(
    'a',
    list(range(1,11))
)
