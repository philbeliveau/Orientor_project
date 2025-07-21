> I don't want you to push the commit yet, I want you to solve these error first: 

# Issue 1                                                                                 │
│   You have an error here:\                                                                                                                                                      │
│   The real router is here: backend/dev/competenceTree_dev\                                                                                                                      │
	size mismatch for encoder.conv1.lin_l.weight: copying a param with shape torch.Size([128, 384]) from checkpoint, the shape in current model is torch.Size([256, 384]).

	size mismatch for encoder.conv1.lin_l.bias: copying a param with shape torch.Size([128]) from checkpoint, the shape in current model is torch.Size([256]).

	size mismatch for encoder.conv1.lin_r.weight: copying a param with shape torch.Size([128, 384]) from checkpoint, the shape in current model is torch.Size([256, 384]).

	size mismatch for encoder.norm1.weight: copying a param with shape torch.Size([128]) from checkpoint, the shape in current model is torch.Size([256]).

	size mismatch for encoder.norm1.bias: copying a param with shape torch.Size([128]) from checkpoint, the shape in current model is torch.Size([256]).

	size mismatch for encoder.norm1.running_mean: copying a param with shape torch.Size([128]) from checkpoint, the shape in current model is torch.Size([256]).

	size mismatch for encoder.norm1.running_var: copying a param with shape torch.Size([128]) from checkpoint, the shape in current model is torch.Size([256]).

	size mismatch for encoder.conv2.lin_l.weight: copying a param with shape torch.Size([128, 128]) from checkpoint, the shape in current model is torch.Size([128, 256]).

	size mismatch for encoder.conv2.lin_r.weight: copying a param with shape torch.Size([128, 128]) from checkpoint, the shape in current model is torch.Size([128, 256]).

ERROR:graph_traversal_service:Le fichier du modèle n'existe pas: /app/dev/app/services/GNN/best_model_20250520_022237.pt

WARNING:graph_traversal_service:Le fichier des indices des types d'arêtes n'existe pas: /app/dev/competenceTree_dev/data/edge_type_indices.json

/app/main_deploy.py:2532: DeprecationWarning: 

        on_event is deprecated, use lifespan event handlers instead.

 

        Read more about it in the

        [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).

# Issue 2
INFO:     Application startup complete.

INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)

INFO:     100.64.0.2:49499 - "GET /health HTTP/1.1" 200 OK

ERROR:app.services.Oasisembedding_service:Le module de formatage OaSIS n'existe pas au chemin: /scripts/format_user_profile_oasis_style.py

INFO:app.routers.profiles:✅ OaSIS embedding service available

INFO:app.routers.profiles:✅ ESCO embedding service available

INFO:app.routers.profiles:✅ Peer matching service available

INFO:app.routers.profiles:Profiles router module loaded with unified authentication

# Issue 3
/root/.local/lib/python3.11/site-packages/pydantic/_internal/_config.py:318: UserWarning: Valid config keys have changed in V2:

* 'orm_mode' has been renamed to 'from_attributes'

  warnings.warn(message, UserWarning)

/root/.local/lib/python3.11/site-packages/pydantic/_internal/_fields.py:149: UserWarning: Field "model_used" has conflict with protected namespace "model_".

 

You may be able to resolve this warning by setting `model_config['protected_namespaces'] = ()`.

  warnings.warn(

WARNING:app.services.Swipe_career_recommendation_service:Career recommendation model not found at /app/app/models/career_recommender_model.pkl, using fallback method

ERROR:app.services.graphsage_llm_integration:Error initializing GraphSage model: Error(s) in loading state_dict for CareerTreeModel:


# Issue 4
NFO:     100.64.0.3:17788 - "POST /api/v1/education/programs/search HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "GET /user-progress/ HTTP/1.1" 200 OK

INFO:     100.64.0.5:59042 - "OPTIONS /api/v1/careers/recommendations?limit=30 HTTP/1.1" 200 OK

ERROR:app.routers.user:JWT decode error: Not enough segments

INFO:     100.64.0.5:59042 - "GET /api/v1/careers/recommendations?limit=30 HTTP/1.1" 401 Unauthorized

INFO:     100.64.0.5:59042 - "OPTIONS /api/v1/careers/saved HTTP/1.1" 200 OK

# Issue 5


INFO:     100.64.0.5:59042 - "GET /user-progress/ HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "GET /api/v1/jobs/saved HTTP/1.1" 200 OK

ERROR:app.routers.user:JWT decode error: Not enough segments

INFO:     100.64.0.5:55482 - "GET /api/v1/careers/saved HTTP/1.1" 401 Unauthorized

                                        last_message_at, message_count, total_tokens_used)

                VALUES (%(user_id)s, %(title)s, %(auto_generated_title)s, 

                       %(last_message_at)s, %(message_count)s, %(total_tokens_used)s)

                RETURNING id, created_at, updated_at;

            ]

[parameters: {'user_id': 55, 'title': 'New Conversation', 'auto_generated_title': True, 'last_message_at': datetime.datetime(2025, 7, 21, 17, 57, 20, 852721), 'message_count': 1, 'total_tokens_used': 0}]

(Background on this error at: https://sqlalche.me/e/20/gkpj)

ERROR:app.services.socratic_chat_service:Error in Socratic chat service: (psycopg2.errors.NotNullViolation) null value in column "id" of relation "conversations" violates not-null constraint

DETAIL:  Failing row contains (null, 55, New Conversation, t, null, f, f, 2025-07-21 17:57:20.548226+00, 2025-07-21 17:57:20.548226+00, 2025-07-21 17:57:20.852721+00, 1, 0).

 

[SQL: 

                INSERT INTO conversations (user_id, title, auto_generated_title, 

                                        last_message_at, message_count, total_tokens_used)

                VALUES (%(user_id)s, %(title)s, %(auto_generated_title)s, 

                       %(last_message_at)s, %(message_count)s, %(total_tokens_used)s)

                RETURNING id, created_at, updated_at;

            ]

[parameters: {'user_id': 55, 'title': 'New Conversation', 'auto_generated_title': True, 'last_message_at': datetime.datetime(2025, 7, 21, 17, 57, 20, 852721), 'message_count': 1, 'total_tokens_used': 0}]

(Background on this error at: https://sqlalche.me/e/20/gkpj)
INFO:     100.64.0.5:59026 - "POST /api/v1/socratic-chat/send HTTP/1.1" 500 Internal Server Error


# Issue 6 
NFO:     100.64.0.5:55482 - "GET /user-progress/ HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "OPTIONS /api/v1/profiles/me HTTP/1.1" 200 OK

INFO:app.routers.profiles:Attempting to get profile for user ID: 55

INFO:app.routers.profiles:No profile found for user ID: 55, creating a new one

INFO:     100.64.0.5:60316 - "GET /api/v1/career-goals/active HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "GET /api/v1/profiles/me HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "OPTIONS /api/v1/profiles/update HTTP/1.1" 200 OK

INFO:     100.64.0.5:60330 - "GET /user-progress/ HTTP/1.1" 200 OK

INFO:app.routers.profiles:Attempting to update profile for user ID: 55

INFO:     100.64.0.3:17778 - "GET /api/tests/holland/user-results HTTP/1.1" 200 OK

INFO:app.routers.profiles:Updating profile fields: ['name', 'age', 'sex', 'major', 'year', 'gpa', 'hobbies', 'country', 'state_province', 'unique_quality', 'story', 'favorite_movie', 'favorite_book', 'favorite_celebrities', 'learning_style', 'interests', 'job_title', 'industry', 'years_experience', 'education_level', 'career_goals', 'skills']

ERROR:app.routers.profiles:Error updating profile: (psycopg2.errors.NotNullViolation) null value in column "id" of relation "user_skills" violates not-null constraint

INFO:     100.64.0.3:56846 - "GET /api/v1/avatar/me HTTP/1.1" 200 OK

DETAIL:  Failing row contains (null, 55, null, null, null, null, null, 2025-07-21 17:57:12.026177+00, null, null, null, null, null, null, null, null).

 

INFO:     100.64.0.3:56876 - "GET /api/v1/courses HTTP/1.1" 200 OK

[SQL: INSERT INTO user_skills (user_id, creativity, leadership, digital_literacy, critical_thinking, problem_solving, analytical_thinking, attention_to_detail, collaboration, adaptability, independence, evaluation, decision_making, stress_tolerance) VALUES (%(user_id)s, %(creativity)s, %(leadership)s, %(digital_literacy)s, %(critical_thinking)s, %(problem_solving)s, %(analytical_thinking)s, %(attention_to_detail)s, %(collaboration)s, %(adaptability)s, %(independence)s, %(evaluation)s, %(decision_making)s, %(stress_tolerance)s) RETURNING user_skills.id, user_skills.last_updated]

INFO:     100.64.0.3:17778 - "GET /api/v1/jobs/recommendations/me?top_k=3 HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "POST /api/v1/education/programs/search HTTP/1.1" 200 OK

# Issue 7 
INFO:     100.64.0.5:60314 - "GET /api/v1/space/notes HTTP/1.1" 200 OK

[parameters: {'user_id': 55, 'creativity': None, 'leadership': None, 'digital_literacy': None, 'critical_thinking': None, 'problem_solving': None, 'analytical_thinking': None, 'attention_to_detail': None, 'collaboration': None, 'adaptability': None, 'independence': None, 'evaluation': None, 'decision_making': None, 'stress_tolerance': None}]

(Background on this error at: https://sqlalche.me/e/20/gkpj)

INFO:     100.64.0.5:59026 - "PUT /api/v1/profiles/update HTTP/1.1" 500 Internal Server Error

INFO:     100.64.0.5:59026 - "GET /user-progress/ HTTP/1.1" 200 OK

INFO:     100.64.0.5:60300 - "GET /api/v1/jobs/saved HTTP/1.1" 200 OK

INFO:     100.64.0.5:60302 - "GET /user-progress/ HTTP/1.1" 200 OK

# Issue 8 
INFO:     100.64.0.5:59026 - "GET /user-progress/ HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "OPTIONS /api/v1/socratic-chat/send HTTP/1.1" 200 OK

ERROR:app.services.conversation_service:Error creating conversation: (psycopg2.errors.NotNullViolation) null value in column "id" of relation "conversations" violates not-null constraint

DETAIL:  Failing row contains (null, 55, New Conversation, t, null, f, f, 2025-07-21 17:57:20.548226+00, 2025-07-21 17:57:20.548226+00, 2025-07-21 17:57:20.852721+00, 1, 0).

 

[SQL: 

                INSERT INTO conversations (user_id, title, auto_generated_title, 

INFO:     100.64.0.5:60314 - "OPTIONS /api/v1/jobs/recommendations/me?top_k=30&embedding_type=esco_embedding HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "GET /user-progress/ HTTP/1.1" 200 OK

INFO:     100.64.0.3:17778 - "GET /api/v1/jobs/recommendations/me?top_k=30&embedding_type=esco_embedding HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "GET /user-progress/ HTTP/1.1" 200 OK

# Issue 9 


INFO:     100.64.0.5:59026 - "GET /api/v1/space/notes HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "OPTIONS /api/v1/courses/1 HTTP/1.1" 200 OK

INFO:     100.64.0.3:56860 - "GET /api/v1/courses/1 HTTP/1.1" 404 Not Found

INFO:     100.64.0.3:56860 - "GET /api/v1/courses HTTP/1.1" 200 OK

INFO:     100.64.0.5:59026 - "GET /peers/compatible HTTP/1.1" 200 OK

# Issue 10
INFO:     100.64.0.4:59164 - "GET /api/v1/insight/get HTTP/1.1" 404 Not Found

# Issue 11
INFO:     100.64.0.4:59156 - "GET /v1/competence-tree/anchor-skills HTTP/1.1" 404 Not Found

# Issue 12
INFO:     100.64.0.4:59156 - "POST /api/v1/insight/generate HTTP/1.1" 404 Not Found

# Issue 13
FO:     100.64.0.5:16422 - "GET /peers/compatible HTTP/1.1" 200 OK

INFO:     100.64.0.3:46346 - "GET /api/v1/insight/get HTTP/1.1" 404 Not Found

INFO:     100.64.0.4:62002 - "GET /api/tests/holland/user-results HTTP/1.1" 200 OK

# Issue 14 
:     100.64.0.5:57602 - "OPTIONS /api/v1/careers/recommendations?limit=30 HTTP/1.1" 200 OK

INFO:     100.64.0.5:57602 - "GET /user-progress/ HTTP/1.1" 200 OK

ERROR:app.routers.user:JWT decode error: Not enough segments

INFO:     100.64.0.5:57602 - "GET /api/v1/careers/recommendations?limit=30 HTTP/1.1" 401 Unauthorized

INFO:     100.64.0.5:40386 - "GET /user-progress/ HTTP/1.1" 200 OK

ERROR:app.services.conversation_service:Error creating conversation: (psycopg2.errors.NotNullViolation) null value in column "id" of relation "conversations" violates not-null constraint

DETAIL:  Failing row contains (null, 55, New Conversation, t, null, f, f, 2025-07-21 18:05:20.350257+00, 2025-07-21 18:05:20.350257+00, 2025-07-21 18:05:20.567065+00, 1, 0).

 

[SQL: 

                INSERT INTO conversations (user_id, title, auto_generated_title, 

                                        last_message_at, message_count, total_tokens_used)

                VALUES (%(user_id)s, %(title)s, %(auto_generated_title)s, 

                       %(last_message_at)s, %(message_count)s, %(total_tokens_used)s)

                RETURNING id, created_at, updated_at;

            ]

[parameters: {'user_id': 55, 'title': 'New Conversation', 'auto_generated_title': True, 'last_message_at': datetime.datetime(2025, 7, 21, 18, 5, 20, 567065), 'message_count': 1, 'total_tokens_used': 0}]

(Background on this error at: https://sqlalche.me/e/20/gkpj)

ERROR:app.services.socratic_chat_service:Error in Socratic chat service: (psycopg2.errors.NotNullViolation) null value in column "id" of relation "conversations" violates not-null constraint

DETAIL:  Failing row contains (null, 55, New Conversation, t, null, f, f, 2025-07-21 18:05:20.350257+00, 2025-07-21 18:05:20.350257+00, 2025-07-21 18:05:20.567065+00, 1, 0).

 

[SQL: 

                INSERT INTO conversations (user_id, title, auto_generated_title, 

                                        last_message_at, message_count, total_tokens_used)

                VALUES (%(user_id)s, %(title)s, %(auto_generated_title)s, 

                       %(last_message_at)s, %(message_count)s, %(total_tokens_used)s)

                RETURNING id, created_at, updated_at;

            ]

[parameters: {'user_id': 55, 'title': 'New Conversation', 'auto_generated_title': True, 'last_message_at': datetime.datetime(2025, 7, 21, 18, 5, 20, 567065), 'message_count': 1, 'total_tokens_used': 0}]

(Background on this error at: https://sqlalche.me/e/20/gkpj)

INFO:     100.64.0.5:40386 - "POST /api/v1/socratic-chat/send HTTP/1.1" 500 Internal Server Error

# Issue 15 
INFO:     100.64.0.3:46510 - "GET /peers/refresh HTTP/1.1" 404 Not Found

INFO:     100.64.0.5:27028 - "GET /health HTTP/1.1" 200 OK

ERROR:app.routers.user:JWT decode error: Not enough segments

INFO:     100.64.0.4:41290 - "GET /api/v1/careers/recommendations?limit=30 HTTP/1.1" 401 Unauthorized

INFO:     100.64.0.3:49450 - "GET /health HTTP/1.1" 200 OK

🔧 Connecting to database...

✅ user_profiles table already exists

INFO:     100.64.0.3:22334 - "POST /admin/create-tables HTTP/1.1" 200 OK

ERROR:app.routers.user:JWT decode error: Not enough segments

INFO:     100.64.0.3:22386 - "GET /api/v1/careers/recommendations?limit=30 HTTP/1.1" 401 Unauthorized

ERROR:app.utils.auth:🚨 Email mismatch: token=test@example.com, db=beli29@example.com

ERROR:app.utils.auth:❌ Authentication error: 

ERROR:__main__:❌ Error in /careers/saved alias: 

ERROR:__main__:❌ Full traceback: Traceback (most recent call last):

  File "/app/app/utils/auth.py", line 74, in get_current_user_unified

    raise HTTPException(status_code=401, detail="Token validation failed")

fastapi.exceptions.HTTPException

 

During handling of the above exception, another exception occurred:

 

Traceback (most recent call last):

  File "/app/main_deploy.py", line 2170, in get_careers_saved_alias

    current_user = await get_current_user_unified(authorization, db)

                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/app/app/utils/auth.py", line 84, in get_current_user_unified

    raise HTTPException(status_code=401, detail="Authentication failed")

fastapi.exceptions.HTTPException

 

INFO:     100.64.0.3:56668 - "GET /careers/saved HTTP/1.1" 500 Internal Server Error

INFO:     100.64.0.4:52366 - "OPTIONS /peers/compatible HTTP/1.1" 200 OK

