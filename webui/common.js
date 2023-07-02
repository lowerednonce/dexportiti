"use strict"

async function read_local_JSON(filename) {
    try {
        const response = await fetch(filename);
        let json_data = await response.json();
        return json_data;
    } catch (error) {
        console.error('Error reading server data from local JSON: ', error);
        alert("There was an error reading the local save from the selected server.");
    }
}

function convert_date(timestamp){
    if (timestamp == "None") { // TODO: look into this more
        return "Invalid date";
    }
    const date = new Date(parseInt(timestamp)*1000)
    return ("0" + date.getDate()).slice(-2)     + "/"
        + ("0" + (date.getMonth()+1)).slice(-2) + "/"
        + date.getFullYear()                    + " "
        + ("0" + date.getHours()).slice(-2)     + ":"
        + ("0" + date.getMinutes()).slice(-2)   + ":"
        + ("0" + date.getSeconds()).slice(-2);
    // DD/MM/YYYY HH:MM:SS
    // the ("" + part).slice(-2) is to add a leading zero
    // if it doesn't need a leading zero, it is sliced out
}

function extract_avatar_url(user) {
    if(user.avatar != null) {
        return "../" + SERVER_ID + "/assets/" + user["avatar"]["key"] + ".png";
    } else {
        // in case there is no avatar set, use the one provided by Discord
        return "../" + SERVER_ID + "/assets/" + user["default_avatar"]["key"] + ".png";
    }
}

function extract_emoji_url(emoji) {
  return "../" + SERVER_ID + "/emojis/" + emoji.id + (emoji.animated ? ".gif" : ".png");
}
