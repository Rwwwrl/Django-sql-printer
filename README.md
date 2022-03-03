## SqlPrinter

Нужен для принтов _sql_-кода, которые генерирует джанго.

#### Использование

1. Использование в качестве **декоратора**:

```python

@PrintSqlTool()
def some_func():
    ...
    models.SomeModel.objects.first()
    ...
    models = models.SomeModel.objects.all()
    models_data = get_models_data(models)
    ...

    return smth
```

В этом случае мы увидим все запросы, которые проходили в функции

2. Использование в качестве **контекстного менеджера**

```python

def some_func():
    ...
    models.SomeModel.objects.first()
    ...
    with PrintSqlTool():
        models = models.SomeModel.objects.all()
        models_data = get_models_data(models)
    ...

    return smth
```

В этом случае мы увидим все запросы, которые были выполнены внутри блока контекстного менеджера.
