# llm_wordle
Challenges for LLM

# Building
In one terminal run `pip install -r requirements.txt`, then `uvicorn users:app --reload`

To build the javascript and move everything into the correct static directory run `./build.sh`. Rerun this to rebuild the js. This needs `npm`

To just mess with the templates and not touch the JS run: `npx tailwindcss -i ./assets/css/styles.css -o ./app/static/css/styles.css --watch`

