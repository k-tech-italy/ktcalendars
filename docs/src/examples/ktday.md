# KTDay

See example usages


## Comparison

You can compare a KTDay with another KTDay or another date
```python
KTDay('2025-06-02') == KTDay('2025-06-02')
KTDay('2025-06-02') != KTDay('2025-06-03')
KTDay('2025-06-02') == dt('2025-06-02')
KTDay('2025-06-02') != dt('2025-06-03')

KTDay('2025-06-02') > KTDay('2025-06-02')
KTDay('2025-06-03') > KTDay('2025-06-02')
KTDay('2025-06-01') >= KTDay('2025-06-02')
KTDay('2025-06-02') >= KTDay('2025-06-02')
KTDay('2025-06-03') >= KTDay('2025-06-02')
KTDay('2025-06-02') > datetime.date('2025-06-02')
KTDay('2025-06-03') > datetime.date('2025-06-02')
KTDay('2025-06-01') >= datetime.date('2025-06-02')
KTDay('2025-06-02') >= datetime.date('2025-06-02')
KTDay('2025-06-03') >= datetime.date('2025-06-02')
```
