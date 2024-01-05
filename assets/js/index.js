import Alpine from "alpinejs";

window.Alpine = Alpine;

Alpine.data('llm_challenge', () => ({

    error: "",

    name: "",
    description: "",
    input: "",
    challenge_id: -1,
    challenge_loaded: false,
    number_of_loaded_challenges: 0,
    challenge_first_load: true,

    models: [],
    selected_model: "",

    output: "Generated Text",
    reason: "",
    generation_id: -1,

    showing_submission: false,
    showing_report: false,
    submission_window: false,
    submission_text: "",
    is_report: false,

    async init() {
        await this.new_challenge();
    },

    async select_model(model) {
        this.selected_model = model;
    },

    async close_error() {
        this.error = "";
    },

    async new_challenge() {
        const response = await fetch("/api/challenge", {credentials: 'include'});
        if (response.status == 429) { 
            this.error = "Too many challenge requests! Slow down.";
            return;
        };
        if (response.status != 200) {
            this.error = "Something went wrong. Please try again later.";
        };
        const data = await response.json();
        if (data.error) {
            this.error = data.error;
            return;
        }

        this.challenge_id = data.id;
        this.name = data.name;
        this.description = data.description;
        if (this.challenge_id == -1) {
            this.challenge_loaded = false;
        } else {
            this.challenge_loaded = true;
            this.number_of_loaded_challenges += 1;
        };
        if (this.number_of_loaded_challenges > 0) {
            this.challenge_first_load = false;
        }
    },

    async clear() {
        this.input = "";
        this.output = "Generated Text";
        this.generation_text = "";
        this.reason = "";
        this.generation_id = -1;
        this.submission_text = "";
        this.submission_window = false;
        this.error = "";
    },

    async generate(model) {
        if (this.input == "") {
            this.error = "Please enter a prompt.";
            return;
        }
        if (this.challenge_id == -1) {
            this.error = "Please wait for a challenge.";
        }

        this.generation_text = "Generating...";
        const response = await fetch("/api/generate/" + this.challenge_id, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            body: JSON.stringify({
                prompt: this.input,
                model: model,
            })
        });
        if (response.status == 429) {
            this.error = "System is overloaded. Please wait a few seconds before generating again.";
        }
        if (response.status != 200) {
            this.error = "Something went wrong. Please try again later.";
        };
        const data = await response.json();
        if (data.error) {
            this.error = data.error;
            return;
        }
        this.generation_text = "";
        this.output = data.generation;
        this.generation_id = data.id;
    },

    async show_submission(is_report) {
        if (this.generation_id == -1) {
            this.error = "Please generate text first.";
            return;
        }
        if (is_report) {
            this.submission_text = "Tell us why this is inappropriate.";
            this.showing_report = true;
            this.showing_submission = false;
        } else {
            this.submission_text = "Tell us why this satisfies the challenge.";
            this.showing_submission = true;
            this.showing_report = false;
        };
        this.is_report = is_report;
        this.submission_window = true;
    },

    async close_submission() {
        console.log("closing");
        this.submission_window = false;
        this.submission_text = "";
        this.thank_you = true;
        this.showing_submission = false;
        this.showing_report = false;
    },

    async submit(new_challenge) {
        console.log("submitting");
        if (this.generation_id == -1) {
            this.error = "Please generate text first.";
            return;
        };
        if (this.reason == "") {
            this.error = "Please enter a reason.";
            return;
        };
        const response = await fetch("/api/submit/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            body: JSON.stringify({
                generation_id: this.generation_id,
                reason: this.reason
            })
        });
        if (response.status == 429) {
            this.error = "You can only submit one generation a minute. Please wait a bit.";
        };
        if (response.status != 200) {
            this.error = "Something went wrong. Please try again later.";
        };

        const data = await response.json();
        if (data.error) {
            this.error = data.error;
            return;
        }

        this.submission_text = data.message;
        await this.close_submission();
        if (new_challenge) {
            await this.new_challenge();
        };
        await this.clear();
    }
}));

Alpine.start();