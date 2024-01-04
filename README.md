# llm_wordle
Challenges for LLM

We have 3 models (plus a bonus!) for evaluation and comparison. They're all small and not nearly as powerful as Gemini or ChatGPT. The three models differ in their safety guarantees and design.
We have Mixtral 7b which has no Reinforcement Learning from Human Feedback (RLHF), Llama2 which has a lot of RLHF, and a Llama2 with a firewall to block prompt injections.
They all perform similarly on benchmarks, but you'll quickly see the differences in security.
Reinforcement Learning from Human Feedback (and it's cousins) is designed to train the model to respond more appropriately in a variety of cases. 
Models that have gone through this process produce less toxic content, and are a minimum for something we'd recommend for a deployment that may have kids interacting with the model.
However, a model needs a lot of RLHF to protect against prompt injection. 
Too much RLHF for prompt injection tends to create a less capable model that's more frustrating to end users. 
So, many use a secondary model to double check the primary. 
We're using Robust Inteligence's AI Firewall for this, but there are several other options. 

So, get a feel for what each type of protection does and see if you can break the Llama2 with guardrails! Please report the findings on the hardest model, which we'll be reviewing for the discussion after lunch.


# Building
Copy `.env_dev.template` to `.env_dev`.  Then run `./build.sh` followed by `docker compose -f dockers/docker-compose.dev.yml up --build` in one terminal. In another terminal run `./build.sh` to update the JavaScript, or `npx tailwindcss -i ./assets/css/styles.css -o ./app/static/css/styles.css --watch` to work on the CSS.

