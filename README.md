# QBag Backend

_This project serves as backend for [QBag frontend](https://github.com/Team-Executables/qbag-frontend)._

_Question Bank Generator uses a crowd sourcing model to prepare question banks from a large pool of objective questions. QBaG provides an interface for paper setters and academicians to generate reliable question papers using our automated and robust system. The questions can be selected based on a range of parameters and can be exported to your desired format within minutes. Each question contributed is passed through a number of checks and is also vetted by experts._

<br/>

**Link to the website:** []()
<br/>
**Link to frontend repo:** [https://github.com/Team-Executables/qbag-frontend](https://github.com/Team-Executables/qbag-frontend)
<br/>
**Link to project presentation:** [[https://github.com/Team-Executables/qbag-frontend](https://github.com/Team-Executables/qbag-frontend/blob/main/Question%20Bank%20Generator.pdf)]([https://github.com/Team-Executables/qbag-frontend](https://github.com/Team-Executables/qbag-frontend/blob/main/Question%20Bank%20Generator.pdf))


### Tech Stack ###
* Material UI v5.1.1
* ReactJS v17.0.2
* RestAPI
* PyTorch v1.11.0
* Django v4.0.3


### API Endpoints ###
**Authentication:**
| Method | URL | Description |
| :---         | :---         | :---         
| `POST`   | `/auth/register`     | To register or sign-up user (teacher and other)    |
| `GET`     | `/auth /email-verify`       |  To verify user's email      |
| `POST`     | `/auth/login`       |  To log into QBag     |
| `POST`     | `/auth/token/refresh`       | To refresh access token by sending refresh token      |
| `POST`     | `/auth/logout`       |    To log out from QBag   |
| `PATCH/PUT`     | `/auth/change-password`       | To change user’s password      |
| `POST`     | `/auth/request-reset-email`       | To post email to get password reset link      |
| `GET` | `/auth/password-reset/{uidb64}/{token}` | To Verify User using uidb64 and token |
| `GET` | `/auth /password-reset-confirm` | To confirm new password |
| `PATCH` | `/auth /password-reset-complete` | To set new password |

<br/>

**Questions:**
| Method | URL | Description |
| :---         | :---         | :--- 
| `POST` | `/questions/create-question` | Used by user to create question |
| `GET` | `/questions/get-question` | Used by teacher to get a question |
| `POST` | `/questions/retrieve-question` | Used by teacher to retrieve a question  |
| `POST` | `/questions/get-similar-questions` | Used by user to get similar questions |
| `POST` | `/questions/vote-question` | Used by teacher to upvote or downvote a question |
| `POST` | `/questions/create-paper` | Used by teacher to create paper from selected questions |
| `GET` | `/questions/all-papers` | Used bt teacher to get all papers created by teacher |
| `GET` | `/questions/questions-from-paper` | Used by teacher get questions from paper created |

<br/>

<br/>
<br/>
