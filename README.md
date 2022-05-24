### Привет. Это - тренажёр базовых элементов блокчейна 

Всё это поможет разобраться как на самом базовом уровне работает блокчейн. Перед изучением рекомендуется ознакомиться с базовыми понятиями блокчейна самостоятельно
### Подготовка / Python

Установите Python версии 3.6 и выше, воспользовавшись инструкциями по установке по адресу [https://www.python.org/](https://www.python.org/). Код написан на версии 3.8

Не забудьте установить менеджер пакетов pip. После успешной установки переместитесь в терминале на каталог с проектом и выполните следующую команду

```
pip install pipenv
```


Откройте проект и установите необходимые зависимости, воспользовавшись  установленным ранее менеджером виртуальных окружений pipenv.

```
pipenv --python=Х
pipenv install
```
где Х - это путь к питоновскому файлу вашей версии, например "C:\Users\Grechka\AppData\Local\Programs\Python\Python38-32\python.exe"

После применения команд выше, в вашем проекте должны были создаться файлы *Pipfile* и *Pipfile.lock*, в некоторых случаях и *requirements.txt*. Если при выполнении команд выдаётся ошибка, то воспользуйтесь , сначала проделайте следующий шаг. Если всё равно не будет работать, то загуглите ошибку и почините её, всё гуглится :)

### Подготовка / Flask, Junja2 и Requests

Все перечисленные выше библиотеки необходимы для работы и их стоит установить любыми известными для вас способами, например
```
pip install Flask==2.1.2 requests==2.27.1
pip install Jinja2==3.1.2
```

**Рекомендую** использовать те версии, которые я указываю, так как некоторые версии друг с другом не коннектятся. Если выходят запросы на подгрузку других библиотек, которых у вас возможно нет, смело устанавливайте

### Подготовка / Postman

Эта штука нужна, чтобы отправлять запросы и получать ответы от сервера. Postman - крутой HTTP клиент для работы с API

Скачать Postman 👉 https://www.postman.com/

Туториал по пользованию на youtube 👉 https://youtu.be/Qe-kDHq-Vw4


### Разбираемся с кодом / Блокчейн

В программе существует только 1 класс Blockchain, который представляет наш блокчейн и имеет следующие функции:

* функция `last_block` возвращает последний блок в цепи;

* функция `new_transaction` добавляет новую транзакцию в список транзакций, ожидающих подтверждения;

* функция `new_block` создает новый блок на основе последнего известного блока, списка транзакций и доказательства работы; 

* функция `hash` считает хеш переданного ей блока алгоритмом _sha256_;

* функции `proof_of_work`, `valid_proof`, `valid_chain` и `resolve_conflicts` нужны для достижения консенсуса — об этом будет рассказано далее.

* функция `register_node` необходима для поддержания распределённых сетей, создаёт новые узлы

### Разбираемся с кодом / Блокчейн / Блоки

Блок — запись, содержащая в себе следующие поля:

* `index` — порядковый номер блока. Первый блок в блокчейне называется генезисом и имеет порядковый номер 1;

* `timestamp` — дата и время создания блока;

* `previous_hash` — хеш предыдущего блока — основа связности блокчейна;

* `transactions` — данные о транзакциях, хранящихся в блоке;

* `proof` — доказательство работы (proof of work)

### Разбираемся с кодом / Блокчейн / Доказательство работы и консенсус

Блокчейн — хранилище данных, представленное как цепочка из блоков. Для того, чтобы хранить данные распределенно, необходимо разработать **алгоритм консенсуса**, который бы мог выявлять, какая из двух различных цепочек является актуальной на данный момент. Так как удалять информацию из цепочки нельзя, простейшей имплементацией алгоритма консенсуса было бы *считать актуальной наиболее длинную цепочку блоков*. Однако, данный алгоритм может быть атакован мошенниками, используя две ветви транзакций, в нужный момент сделав публичной ветвь, держащуюся в тени и имеющую большее количество транзакций, таким образом, затерев публичную до этого ветку. 

Для предотвращения подобных атак был придуман алгоритм **proof of work**. Данный алгоритм представляет собой задачу, которую сложно решить, но легко проверить ее решение. В качестве такой задачи может быть использована следующая: *"Найти число (proof) при подстановке которого в блок его хеш по алгоритму sha256 имеет на конце N нолей"*. Варьируя значение *N*, мы можем управлять сложностью алгоритма с изменением количества мощностей, участвующих в блокчейне.

В  демонстрации блокчейна уже есть следующие функции:

* функция `proof_of_work` находит требуемое доказательство перебором, начиная от 0;

* функция `valid_proof` проверяет правильность полученного доказательства;

* функция `resolve_conflicts` принимает две цепочки и сохраняет как актуальную наибольшую валидную цепочку из двух.

### Как с этим работать? Запуск
Для запуска сервера введи в терминал следующую команду,  заменив ПОРТ на номер желаемого сетевого порта

```
pipenv run python blockchain.py --port ПОРТ
```


Проверив, что после запуска сервера GET запрос на _localhost:ПОРТ/ping_ возвращает код _200 OK_, можно приступать к следующим шагам

!["запрос ping"](https://i.imgur.com/eP18bn5.jpeg)


### Как с этим работать? / Пользователи распределённой сети
Весь тренажёр построен на распределённой сети, которая реализуется через локальные порты. Представим, что сейчас в цепи только 2 пользователя с разными портами. Для примера, у меня это порт 5000 и 5002

Возникает логичный вопрос, а как запустить сервер на 2 порта? Создать новую сессию в терминале и ввести соотвествующую команду для запуска на втором порту :)

!["запуск на 2-х портах"](https://i.imgur.com/sNlgI85.png)

Чтобы добавить ещё пользователей, достаточно открыть новые порты и запустить сессии через них

### Как с этим работать? / Смотрим дефолтное наполнение блокчейна


Для начала посмотрим, что изначально есть в нашем блокчейне, передав следующий запрос:

GET-запрос  на `http://localhost:5000/chain`

!["запрос chain"](https://i.imgur.com/qWBH6kA.png)

Сейчас в нашем блокчейне только один блок без транзакций. Этот блок называется Генезис блок. Генезис блок почти всегда жестко запрограммирован в программном обеспечении приложений, использующих его блокчейн. Это особый случай, когда блок не ссылается на предыдущий блок (как это всегда устроено в блокчейне).

### Как с этим работать? / Регистрируем новых пользователей(узлы)

Просто открыть сессию на других портах недостаточно, нужно сообщить цепи, что у нас есть ещё новый узел

POST-запрос  на `http://localhost:5000/nodes/register`

с телом запроса
```
{
  "nodes": ["http://127.0.0.1:5002"]
   ...и другие порты,если есть...
}
```
Тело запроса необходимо писать в специальное поле во вкладке *Body*

!["запрос на новый узел"](https://i.imgur.com/oiScZN4.png)

После выполнения запроса будет выведено сообщение об удачном добавлении и показан список всех существующих узлов в цепи. Не забудь добавить и второй узел

### Как с этим работать? / Создаём новый блок 

Давай попробуем создать новый блок, запустив процесс майнинга с любого порта

GET-запрос  на `http://localhost:5002/mine`

!["запрос на новый блок"](https://i.imgur.com/F4ke8lC.png)

В результате мы получили новый блок, в котором первая транзакция - вознаграждение майнеру.

### Как с этим работать? / Создаём транзакцию

Теперь пора и отправить монеты :)

POST-запрос  на `http://localhost:5002/transactions/new`
с телом запроса
```
{
	"recipient":"lena",
	"sender":"masha",
	"amount":"30"
}
```
В настоящих блокчейнах конечно нет никаких имён, а указаны адреса, но мы опустим это, так как это не критично для понимания

!["запрос на новую транзакцию"](https://i.imgur.com/Gf7ET82.png)

Если мы сейчас повторим  запрос на вывод всех блоков, то получим следующий вывод

!["запрос на цепочку"](https://i.imgur.com/uJ510ie.png)

"А где наша транзакция от Маши? Куда пропали 30 монеток?"- такой возник вопрос, верно?

Не боимся, это нормально. Дело в том, что, по принципам блокчейна, менять содержимое блоков запрещено. То есть добавить во 2 блок (который мы намайнили перед этим) нашу транзакцию от Маши мы не можем. Наша транзакция никуда не пропала, она хранится в списке необработанных транзакций и ждёт, пока мы не сформируем новый блок. Во многих блокчейнах стоит ограничение на количество транзакций в одном блоке

Давай намайним блок и посмотрим, что получится. Как это сделать? Ищем пункт про создание блоков выше

!["запрос на майнинг блока"](https://i.imgur.com/Mwt1wZN.png)

Ура. Мы создали ещё один блок и в нём есть наша транзакция от Маши,а значит наши 30 монеток не потерялись

Хочу акцентировать внимание, что все действия с созданием новых блоков и транзакций мы проводили через узел с портом 5002. Давай посмотрим, что будет сейчас при запросе всех цепочек. Сделать это можно через тот же самый запрос, через который мы смотрели дефолтное наполнение блока

!["запрос на цепочку 2"](https://i.imgur.com/hfPQyni.png)

Отлично, сейчас у узла 5002 есть все блоки, которые мы создавали и все транзакции в них. А что у узла 5000?

!["запрос на цепочку 3"](https://i.imgur.com/gWZxAAk.png)

Катастрофа. Узел 5000 вообще не вкурсе, что у нас была транзакция от Маши и вообще уже есть 3 блока. Таких ситуаций в реальных блокчейнах естественно не бывает, так как все процессы происходят автоматически, а в этом тренажёре мы инициируем их сами, что понять логику работы блокчейна

Помочь узлу 5000 узнать о том,что было у узла 5002, мы можем с помощью алгоритмов консенсуса. В нашей ситуации это самый известный Proof Of Work. Советую почитать про него

GET-запрос  на `http://localhost:5000/nodes/resolve`

!["консенсус"](https://i.imgur.com/rHYZfeo.png)

Теперь цепочка блоков у узла 5000 заменилась на самую длинную существующую в цепи, которую создал наш узел 5002. То есть 5000 узел знает всё, что делал 5002. Мы можем запустить алгоритм консенсуса и для узла 5002

!["консенсус2"](https://i.imgur.com/ox9IGXl.png)

Как и ожидалось, этот алгоритм ничего не изменял, а просто сообщил нам, что наша цепочка самая актуальная сейчас

И так всегда: если вдруг возникают непреднамеренные развилки в цепочках блоков, то все узлы обновляют свои цепочки до самой длинной

Получается... Это всё! Теперь можно сделать больше узлов и потренироваться. Если хочется попробовать что-то ещё, то можно поработать с кодом, конкретно функцией `mine` и вынести из комментариев код для раздачи ролей узлам. Например, узел 5000 может быть майнером, а 5002 полным узлом

Надеюсь, данный материал помог разобраться в базовых понятиях блокчейна :)
