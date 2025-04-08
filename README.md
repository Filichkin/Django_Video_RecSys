# Django video RecSys 

## Пример приложения Django для поиска похожих видео на основе эмбеддингов

<ol>
<h3>
  <li>
  Добавление возмозможности хранения эмбеддинга видео в БД
  </li>
</h3>


Необходимо установить Extention для PostgreSQL, ссылка на инструкции для различных вариаций:

```
https://github.com/pgvector/pgvector
```

Далее, необходимо установить в окружение библиотеку pgvector:

```
pip install pgvector
```

И внести изменения в файл миграций 0001_initial.py:

```
from pgvector.django import VectorExtension

class Migration(migrations.Migration):
    operations = [
        VectorExtension()
    ]
```

В модель VideoEmbeddings добавляем поле VectorField, для векторного хранения эмбеддинга видео, где dimensions - длина для вектора выдаваемого моделью сети:

```
embedding = VectorField(
        dimensions=EMBEDDING_DIM,
        null=True,
        blank=True
    )
```

Также, переопределяем метод save() для модели, с целью автоматического получения эмбеддинга при загрузке пользователем видео:

```
def save(self, *args, **kwargs):
        self.embedding = get_embedding(self.video)
        super().save(*args, **kwargs)
```
Для повышения производительности загрузки и генерации эмбеддинга, рекомендуется использовать 
celery и декоратор shared_task.

<h3>
  <li>
   Получение эмбеддинга видео
  </li>
</h3>

Для создания эмбеддинга используется модель r2plus1d_18 из контекста библиотеки PyTorch (глубокая сеть R(2+1)D с 18 слоями).

Код алгоритма в файле:

```
video_recsys/video/utils.py
```

Веса и документация предобученной модели находятся по ссылке (требуется 130 Мб для хранения на диске):

<a href="[URL](https://pytorch.org/vision/main/models/generated/torchvision.models.video.r2plus1d_18.html#torchvision.models.video.R2Plus1D_18_Weights)">Модель r2plus1d_18</a>



<h3>
  <li>
   Поиск похожих видео
  </li>
</h3>
</ol>

Алгоритм L2Distance реализован в функции recommended_videos:

```
def recommended_videos(request, uuid):
    """
    Вывод списка похожих видео на основе
    флгоритма L2Distance
    """
    video = get_object_or_404(
        VideoEmbeddings, uuid=uuid
    )
    field_name = 'embedding'
    embedding = getattr(video, field_name)
    recommended_videos = VideoEmbeddings.objects.exclude(uuid=uuid).order_by(
        L2Distance('embedding', embedding)
    )[:RECOMENDED_COUNT]
    return render(
        request,
        'recommendations.html',
        {'recommended_videos': recommended_videos}
    )

```


Некоторые дополнительные функции пакета pgvector.django:
MaxInnerProduct, CosineDistance, L1Distance, HammingDistance и JaccardDistance

**CosineDistance**
Используется для расчёта расстояния (или сходства) между вектором запроса и векторами, хранящимися в базе данных.

**MaxInnerProduct**
Одна из функций, поддерживаемых коннектором Elasticsearch Vector Store для работы с семантическим ядром

**L1Distance**
Позволяет измерять несходство между векторами в многомерном пространстве.

Некоторые особенности L1Distance:

Рассматривает все измерения одинаково и более устойчива к выбросам, чем L2Distance.
Особенно полезна в случаях, когда данные могут содержать значительные шумы или когда масштаб различий по измерениям сильно варьируется.  4
Однако стоит учитывать, что L1Distance может не так эффективно, как L2Distance, измерять истинное геометрическое расстояние в многомерном пространстве.


**Hamming Distance**
Позволяет найти различия между двумя строками или последовательностями одинаковой длины. Она показывает, в каких позициях соответствующие символы отличаются.

Другими словами, Hamming Distance измеряет минимальное количество замен, необходимых для превращения одной строки в другую.

Некоторые области применения Hamming Distance:

Обработка изображений. В анализе изображений и компьютерном зрении Hamming Distance используется для сравнения и распознавания изображений, например, для поиска похожих изображений в базе данных или дубликатов.

**Jaccard distance**
В контексте pgvector — это мера сходства между наборами, которая рассчитывается как отношение пересечения к объединению двух наборов (сколько позиций совпадают из общего количества позиций).

Этот оператор используется для бинарных векторов и доступен в pgvector с версии 0.7.0.

Jaccard distance полезен для сравнения, например, истории покупок клиентов, в рекомендательных системах, для поиска сходства терминов, используемых в разных текстах и т. д