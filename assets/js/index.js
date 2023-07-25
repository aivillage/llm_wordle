import Alpine from "alpinejs";

window.Alpine = Alpine;

Alpine.data('llm_challenge', () => ({
    name: "",
    description: "",
    input: "",
    challenge_id: -1,
    challenge_loaded: false,

    output: "Generated Text",
    generation_text: "",
    reason: "",
    generation_id: -1,
    submission_text: "",

    async init() {
        await this.new_challenge();
    },

    async new_challenge() {
        const response = await fetch("/api/challenge");
        const data = await response.json();
        console.log("Recieved challenge:", data);
        this.challenge_id = data.id;
        this.name = data.name;
        this.description = data.description;
        if (this.challenge_id == -1) {
            this.challenge_loaded = false;
        } else {
            this.challenge_loaded = true;
        };
    },

    async clear() {
        this.input = "";
        this.output = "Generated Text";
        this.generation_text = "";
        this.reason = "";
        this.generation_id = -1;
        this.submission_text = "";
    },

    async generate() {
        if (this.input == "") {
            this.generation_text = "Please enter a prompt.";
            return;
        }
        if (this.challenge_id == -1) {
            this.generation_text = "Please wait for a challenge.";
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
            })
        });
        const data = await response.json();
        this.generation_text = "";
        this.output = data.generation;
        this.generation_id = data.id;
    },

    async submit(report) {
        if (this.generation_id == -1) {
            this.submission_text = "Please generate text first.";
            return;
        };
        if (this.reason == "") {
            this.submission_text = "Please enter a reason.";
            return;
        };
        if (report) {
            var api = "/api/report/";
        } else {
            var api = "/api/submit/";
        }
        const response = await fetch(api, {
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
        const data = await response.json();
        this.submission_text = data.message;
    }
}));

Alpine.start();