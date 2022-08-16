import { resolveBreakpointValues } from "@mui/system/breakpoints";

const wordExam = {
    "word": "amicable",
    "mastered": false,
    "context": [
        "For the most part, these were amicable, but there were occasions when the different priorities of research and product management were visible.",
        "this is another context",
    ],
    "definitions": {
        "Adjective": [
            "(of relations between people) having a spirit of friendliness; without serious disagreement or rancor"
        ]
    }
};

async function api(url, method, payload) {
    let option = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };
    if (payload) {
        option.body = payload
    }
    return await fetch(url, option)
        .then(async function (res) {
            const data = await res.json();
            return {
                success: res.ok,
                ...data
            };
        }).catch(err => {
            return {
                success: false,
                msg: err
            }
        })
}

function recordWord(record) {
    return api("/word", "POST", record);
};

function retriveWords() {
    return api("/word", "GET", null);
}

function retriveDefine(word) {
    return api("/define?word=" + word, "GET", null);
}

function masterWord(word) {
    return api("/master?word=" + word, "PUT", null);
}

export { recordWord, retriveWords, retriveDefine, masterWord };