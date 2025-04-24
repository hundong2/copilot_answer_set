C#에서 JSON Serialize 시 '>' 기호 문제
=======================================

질문
-----

C# 에서 class 구조를 JSON file로 serialize해서 쓰려고 하는데, '>' 부등호 기호가 `\u003E`로 표시가 됩니다. 
나는 '>' 그대로 write하고 싶습니다. 어떻게 해야 하나요?

답변
-----

C#에서 JSON을 직렬화할 때 `>` 기호가 `\u003E`로 변환되는 이유는 JSON 직렬화기에서 HTML 엔코딩을 기본적으로 활성화하기 때문입니다. 이는 XSS(크로스 사이트 스크립트) 공격을 방지하기 위한 보안 조치입니다. 하지만, 원한다면 HTML 엔코딩을 비활성화하여 `>`를 그대로 직렬화할 수 있습니다.

Code Example
------------

.. code-block:: csharp
using Newtonsoft.Json;

class Program
{
    static void Main(string[] args)
    {
        var obj = new
        {
            Example = "1 > 0"
        };

        var settings = new JsonSerializerSettings
        {
            StringEscapeHandling = StringEscapeHandling.Default // HTML 엔코딩 비활성화
        };

        string json = JsonConvert.SerializeObject(obj, settings);
        System.Console.WriteLine(json);
    }
}