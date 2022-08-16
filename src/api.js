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

function deleteWord(word) {
    return api("/word?word="+word, "DELETE", null);
}

function retriveDefine(word) {
    return api("/define?word=" + word, "GET", null);
}

function masterWord(word) {
    return api("/master?word=" + word, "PUT", null);
}


export { recordWord, retriveWords, retriveDefine, masterWord, deleteWord };