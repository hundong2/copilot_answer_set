=========================================
C#에서 Jira Issue 정보 가져오는 방법
=========================================

질문
====
**C# curl로 Jira Issue 정보 가져오는 방법**

설명
====
C#에서 Jira API를 사용하여 Issue 정보를 가져오기 위해서는 ``HttpClient``를 사용하여 REST API 요청을 보내는 방법이 일반적입니다. Jira의 REST API는 기본 인증 또는 OAuth2 인증을 지원하며, 일반적으로 **Basic Authentication**을 사용합니다.

---

준비 사항
==========
1. **Jira API URL**:
   Jira Issue를 가져오는 REST API URL은 다음과 같습니다::
   
     https://<your-jira-domain>.atlassian.net/rest/api/2/issue/{issueKey}
   
   - ``<your-jira-domain>``: Jira 도메인 (예: ``companyname.atlassian.net``)
   - ``{issueKey}``: 가져오려는 Issue의 Key (예: ``PROJ-123``)

2. **인증 정보**:
   - Jira REST API에 접근하려면 인증이 필요합니다. ``Basic Authentication``을 사용하려면 Base64로 인코딩된 사용자 이메일과 API 토큰이 필요합니다.
   - [Jira API 토큰 생성 방법](https://id.atlassian.com/manage-profile/security/api-tokens)을 참고하세요.

---

C# 코드 예제
============

다음은 ``HttpClient``를 사용하여 Jira Issue 정보를 가져오는 코드 예제입니다::

.. code-block:: csharp   
    using System;
    using System.Net.Http;
    using System.Net.Http.Headers;
    using System.Threading.Tasks;

    class Program
    {
        static async Task Main(string[] args)
        {
            // Jira 도메인 및 Issue Key 설정
            string jiraDomain = "your-jira-domain.atlassian.net"; // 예: companyname.atlassian.net
            string issueKey = "PROJ-123"; // Jira Issue Key

            // Jira API URL
            string apiUrl = $"https://{jiraDomain}/rest/api/2/issue/{issueKey}";

            // 사용자 이메일 및 API 토큰
            string username = "your-email@example.com"; // Jira 이메일
            string apiToken = "your-api-token"; // Jira API 토큰

            // Basic Authentication 생성
            string credentials = Convert.ToBase64String(System.Text.Encoding.ASCII.GetBytes($"{username}:{apiToken}"));

            // HttpClient를 사용하여 요청 보내기
            using (HttpClient client = new HttpClient())
            {
                // 인증 헤더 설정
                client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", credentials);

                try
                {
                    // GET 요청 보내기
                    HttpResponseMessage response = await client.GetAsync(apiUrl);

                    // 요청 성공 여부 확인
                    if (response.IsSuccessStatusCode)
                    {
                        // 응답 데이터 읽기
                        string responseData = await response.Content.ReadAsStringAsync();
                        Console.WriteLine("Jira Issue Data:");
                        Console.WriteLine(responseData);
                    }
                    else
                    {
                        Console.WriteLine($"Error: {response.StatusCode}");
                        string errorResponse = await response.Content.ReadAsStringAsync();
                        Console.WriteLine($"Error Details: {errorResponse}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Exception: {ex.Message}");
                }
            }
        }
    }


---

코드 설명
========
1. **API URL 설정**:
   - Jira 도메인과 Issue Key를 기반으로 API URL을 생성합니다::
   
     string apiUrl = $"https://{jiraDomain}/rest/api/2/issue/{issueKey}";

2. **인증 설정**:
   - ``Basic Authentication``을 사용하기 위해 사용자 이메일과 API 토큰을 ``Base64``로 인코딩합니다::
   
     string credentials = Convert.ToBase64String(System.Text.Encoding.ASCII.GetBytes($"{username}:{apiToken}"));
     client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", credentials);

3. **HTTP 요청 보내기**:
   - ``HttpClient.GetAsync``를 사용하여 GET 요청을 보냅니다::
   
     HttpResponseMessage response = await client.GetAsync(apiUrl);

4. **응답 처리**:
   - 요청이 성공하면 응답 데이터를 읽고 출력합니다::
   
     if (response.IsSuccessStatusCode)
     {
         string responseData = await response.Content.ReadAsStringAsync();
         Console.WriteLine(responseData);
     }

---

실행 방법
========
1. 위 코드를 C# 프로젝트에 추가하고, 필요한 패키지가 설치되어 있는지 확인하세요.
2. Jira 이메일, API 토큰, Jira 도메인 및 Issue Key를 적절히 변경하세요.
3. 프로그램을 실행하면 해당 Issue의 JSON 데이터를 출력합니다.

---

샘플 응답 (JSON 데이터)
======================
Jira API에서 반환된 데이터는 JSON 형식입니다. 예::

    {
        "id": "10001",
        "key": "PROJ-123",
        "fields": {
            "summary": "Fix login issue",
            "description": "There is an issue with the login functionality.",
            "status": {
                "name": "In Progress"
            }
        }
    }

---

참고 자료
========
- `Jira REST API Documentation <https://developer.atlassian.com/cloud/jira/platform/rest/v2/>`_
- `HttpClient in C# <https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclient>`_
