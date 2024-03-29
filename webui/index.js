"use strict";

let SERVER_ID = "";

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

async function read_local_slist() {
    try {
        const response = await fetch("export.json");
        let json_data = await response.json();
        return json_data;
    } catch (error) {
        console.error("Error in retrieving server list: ", error);
        alert("There was an error reading the local server list.");
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
        return SERVER_ID + "/assets/" + user["avatar"]["key"] + ".png";
    } else {
        // in case there is no avatar set, use the one provided by Discord
        return SERVER_ID + "/assets/" + user["default_avatar"]["key"] + ".png";
    }
}

function extract_server_icon_html(icon) {
    return "<img id=\"server-icon\" src=\"" + SERVER_ID +  "/assets/" + icon.key + ".png" + "\"></img>"
}

function extract_attachments_html(attachments) {
    const attachments_HTML = attachments.map((e) => {
        if (e.content_type.split("/")[0] == "image") {
            const img_height = (parseInt(e.height) > 500 ) ? 500 : parseInt(e.height);
            const img_width  = (parseInt(e.height) > 500 ) ? e.width/(parseInt(e.height)/500) : e.width;
            return "<img loading=\"lazy\" src=\""
            + SERVER_ID + "/attachments/" + e.id + "-" + e.filename
            + "\" height=\"" + img_height + "\" width=\"" + img_width + "\""
            + " alt=\"" + e.filename + "\"></img>";
        } else if (e.content_type.split("/")[0] == "video") {
            const vid_height = (parseInt(e.height) > 500 ) ? 500 : parseInt(e.height)
            const vid_width  = (parseInt(e.height) > 500 ) ? e.width/(parseInt(e.height)/500) : e.width;
            return "<video height=\"" + vid_height + "\" width=\"" + vid_width + "\" controls>"
                   + "<source src=\"" + SERVER_ID + "/attachments/" + e.id + "-" + e.filename + "\" type=\"" + e.content_type + "\">"
                   + "Unable to display video: no support for \<video\> tag.</video>"
        } else {
            return "<a href=\"" + SERVER_ID + "/attachments/" + e.id + "-" + e.filename + "\">" + e.filename + "</a>";
        }
    })
    .reduce((total, item) => {
        return total + item;
    }, ""); // empty string as the inital value, so an empty list of attachments will return an empty string to the HTML
    return attachments_HTML;
}

function show_message_HTML(cmsg, users, channels) {
    let cmsg_HTML = "<div class=\"cmsg-div\">"
    console.debug("found message: ", cmsg);
    const user = users.filter((user) => {
        return (user.id == cmsg.author || user.id == cmsg.author?.id)
        // sometimes the author is a user object onto itself for some reason
    })[0];
    if (cmsg.type == "MessageType.new_member") {
        cmsg_HTML += "<p class=\"cmsg-content\"> " + "new member: " + user?.display_name??"unknown" + " " +
            (user?.display_name != user?.name ? "(<i>" + user.name + "#" + user.discriminator + "</i>)" : "" ) + "</p>"
                   + "<p class=\"cmsg-timestamp\">(<i>" + convert_date(cmsg.created_at) + "</i>)</p>"
    } else if (cmsg.type == "MessageType.default" || cmsg.type == "MessageType.reply") {
        if (cmsg.type == "MessageType.reply") {
            console.warn("doing a reply, possibly faulty behaviour")
            cmsg_HTML += "<div class=\"cmsg-sender-reply\">"
                            + "<img src=\"" + extract_avatar_url(user) + "\" width=\"64\" height=\"64\"></img>"
                        + "</div>"
                        + "<div class=\"cmsg-content\">"
            const referenced = channels.filter((channel) => {
                return channel.id == cmsg.reference.channel_id
            })[0].messages.filter((message) => {
                return message.id == cmsg.reference.message_id
            })[0]??{}; // fetches message by provided channel_id and message_id, if non-existent, provides empty content

            referenced.author = users.filter((user) => {
                return user.id == referenced?.author;
            })[0];

            cmsg_HTML += "<div class=\"cmsg-reply\">"
                            + (
                                referenced.author == null
                                ? "<p>→ deleted message</p></div>"
                                : "<p>→ " + referenced.author.name + ": " + referenced.content + "</p></div>"  
                            )
                        + "<p class=\"cmsg-author\"><b>" + user.name + "</b></p>"
                        + "<p>" + format_msg_content(cmsg.content, users) + (cmsg.edited_at == null ?  "" : " <i>(edited at " + convert_date(cmsg.edited_at) + ")</i>") + "</p>"
                        + "<div class=\"cmsg-attachments\">" + extract_attachments_html(cmsg.attachments)+ "</div>"
                      + "</div>"
                      + "<p class=\"cmsg-timestamp\">(<i>" + convert_date(cmsg.created_at) + "</i>)</p>"
                      + "</div>"
        } else {
            console.warn("non-reply: normal behaviour expected");
        cmsg_HTML += "<div class=\"cmsg-sender\">"
                        + "<img src=\"" + extract_avatar_url(user) + "\" width=\"64\" height=\"64\"></img>"
                    + "</div>"
                    + "<div class=\"cmsg-content\">"
                      + "<p class=\"cmsg-author\"><b>" + user.name + "</b></p>"
                      + "<p>" + format_msg_content(cmsg.content, users) + (cmsg.edited_at == null ?  "" : " <i>(edited at " + convert_date(cmsg.edited_at) + ")</i>") + "</p>"
                      + "<div class=\"cmsg-attachments\">" + extract_attachments_html(cmsg.attachments)+ "</div>"
                    + "</div>"
                    + "<p class=\"cmsg-timestamp\">(<i>" + convert_date(cmsg.created_at) + "</i>)</p>"
                    + "</div>"
        }
    } else {
        console.warn("unknown message type: ", cmsg.type);
    }
    cmsg_HTML += (cmsg.pinned ? "<p><b><i>(pinned)</i></b></p>" : "") + "</div><hr class=\"cmsg-break\">";
    return cmsg_HTML;
}

function format_msg_content(msg, users) {
    const url_pattern = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
    const mention_pattern = /<@?[0-9]*?>/gim;
    return msg
        .replaceAll("\n", "</br>") // add proper newlines
        .replaceAll(url_pattern, "<a href=\"$&\">$&</a>")
        .replaceAll(mention_pattern, (matched => {
            const user = users.filter((user) => {
                return user.id == matched.slice(2,-1);
            })[0];
            return "<p class=\"cmsg-mention\">@" + user.name + "</p>";
            })
        );
}

let show_members = () => {
    document.getElementById("hide-members").style.display = "flex";
    document.getElementById("show-members").style.display = "none";
    document.getElementsByClassName("users")[0].style.display = "flex";
}

let hide_members = () => {
    document.getElementById("hide-members").style.display = "none";
    document.getElementById("show-members").style.display = "flex";
    document.getElementsByClassName("users")[0].style.display = "none";
}

function gen_cmsg_counter(limit) {
    let counter = 0;
    return [(amount, e) => {
        // setter/event handler
        e.preventDefault();
        if((counter+amount) > limit || (counter+amount)<0){
            console.warn("failed to display more messages");
            console.info("counter at: ", counter, " amount at: ", amount, " limit at: ", limit);
            return
        }else {
            counter += amount;
        }
    },
        // getter, returns the internal variable
        () => {return counter}
    ];
}

read_local_slist().then(data => {
    console.info("parsed server data: ", data);

    data["servers"].map(server => {
        console.log("server option: ", server);
        document.getElementById("sselection-form-list").innerHTML += "<option value=\"" + server.id + "\">" + server.name + "</option>"
    });

})

function show_server(data) {

    // erasing previously loaded HTML
    ["cname","cdesc","cnsfw","cid","ccreated","cmsg_count","cmsg_thread_archive","cmsg_news","cmsg"].map((id) => {
        document.getElementById(id).innerHTML = "";
    });

    // displaying server info
    const parse_list = [
        ["icon",         "",                extract_server_icon_html(data.icon)],
        ["name",         "",                data.name],
        ["id",           "server id: ",     data.id],
        ["created_at",   "creation date: ", convert_date(data["created-at"])],
        ["member_count", "member count: ",  data.members.length],
        ["locale",       "locale: ",        data.preferred_locale],
        ["filesize",     "filesize limit: ",data.filesize_limit/1024 + "Kb"],
        ["export-date",  "export's date: " ,convert_date(data["export-info"]["end-date"])]
    ];
    parse_list.map(pair => {
        document.getElementById(pair[0]).innerHTML = pair[1] + pair[2];
    });

    // loading user info 
    const users_HTML = data["active-users"]
        .map( user => { 
            return "<div class=\"active-member\">"
                + "<img loading=\"lazy\" class=\"active-member-img\" src=\"" + extract_avatar_url(user) + "\" width=\"64\" height=\"64\">"
                + "<p class=\"active-member-username\"><b>"+ user.name + "#" + user.discriminator + (user.bot ? " (bot)" : "") + "</b></p>"
                + "<p class=\"active-member-id\"><i>id: " + user.id + "</i></p>"
                + "<p class=\"active-member-created\">registered: " + convert_date(user.created_at) + "</p>"
                + "<p class=\"active-member-flags\">public flags: " + user.public_flags + "</p>"
                + "</div>";
        })
        .reduce((total, elem) => {
            return total + elem;
        });

    // loading the users HTML as to not bother with it the first time the button is clicked
    document.getElementsByClassName("users")[0].innerHTML = users_HTML; 

    const emojis_HTML = data.emojis
        .map((emoji) => {
            console.log(emoji)
            return "<div class=\"emoji-div\">"
                     + "<div class=\"emoji-image\">"
                         + "<img loading=\"lazy\" src=\"" + SERVER_ID + "/emojis/" + emoji.id + (emoji.animated ? ".gif" : ".png") + "\" height=\"32\" width=\"32\" >"
                     + "</div>"
                     + "<p class=\"emoji-name\">:" + emoji.name + ":</p>"    
                 + "</div>";
        })
        .reduce((total, elem) => {
            return total + elem;
        });

    document.getElementById("emojis").innerHTML = emojis_HTML;
}

function gen_channel_selector(data, filtering) {
    // clojures to get the data object into another lexical scope
    return (e) => {

        e.preventDefault();

        const chn_id = document.getElementById("cselection-form-list").value;
        console.log("working with channel id: ", chn_id);

        const chn = data.channels.filter((channel) => {
            return (channel.id == chn_id)
        })[0];

        console.log(chn);

        const parse_list = [
                ["cname",               "channel name: ",           chn.name + " (" + chn.type + ")" ],
                ["cdesc",               "channel desciption: ",     chn.topic??"<i>not provided</i>"],
                ["cnsfw",               "NSFW: ",                   chn.nsfw ],
                ["cid",                 "id: ",                     "<i>" + chn.id + "</i>"],
                ["ccreated",            "created: ",                convert_date(chn["created_at"])],
                ["cmsg_count",          "total message count: ",    chn.messages?.length??"unapplicable"],
                ["cmsg_thread_archive", "Thread archive default: ", (chn.default_auto_archive_duration/60) + " minutes"], // TODO: Fix NaN in this expression
                ["cmsg_news",           "News: ",                   (chn.is_news ? "yes" : "no")]
        ]

        parse_list.map((line) => {
            document.getElementById(line[0]).innerHTML = line[1] + line[2];
        });

        if(chn.type == "text") {

            // text channel rendering
            document.getElementById("cmsg-btn-down").style.display = "inherit";
            document.getElementById("cmsg-btn-up").style.display = "inherit";

            const cmsg_counters = gen_cmsg_counter(chn.messages.length);
            const cmsg_counter_setter = cmsg_counters[0]; // rather than a setter it increases/decreases the value within a bound
            const cmsg_counter_getter = cmsg_counters[1];

            // console.info((chn["messages"]) == (chn["messages"].sort((e,p) => {return e["created_at"]>["created_at"]})))
            
            
            const render_cmsg = () => {
                console.log("channel render called");
                console.info("slicing channel messages from ", cmsg_counter_getter(), " till ", cmsg_counter_getter()+50);
                document.getElementById("cmsg").innerHTML = chn.messages
                .sort((e,p) => {
                    if (filtering && document.getElementById("fselection-form-sort").checked == true) {
                        // NOTE: this might do an unnessesary element request, but hopefully lazy if evaluation can help
                        return e.created_at<p.created_at;
                    } else {
                        return e.created_at>p.created_at;
                    }
                    // TODO: add option to flip this, ie show from newest to oldest 
                })
                .filter((msg) => {
                    if (filtering) {
                        console.warn("filtering contents, possible unstable behaviour");
                        return msg.content.includes(document.getElementById("fselection-form-search").value);
                    } else {
                        return true;
                    }
                })
                .slice(cmsg_counter_getter(),cmsg_counter_getter()+50)
                .map((message) => {
                    return show_message_HTML(message, data["active-users"], data.channels);
                })
                .reduce((total, e) => {
                    // concatenating the produced HTML
                    return total+e;
                });
            };

            // render the messages for the first time
            render_cmsg();
            
            document.getElementById("cmsg-btn-up").onclick = (e) => {
                cmsg_counter_setter(50, e);
                render_cmsg();
                document.getElementsByClassName("channel-information")[0].scrollIntoView({behavior: "smooth"});
            };
            
            document.getElementById("cmsg-btn-down").onclick = (e) => {
                cmsg_counter_setter(-50, e);
                render_cmsg();
                document.getElementById("cmsg-bottom").scrollIntoView({behavior: "smooth"});
            };       
        } else {
            console.warn("unrecognised channel of type, ", chn.type);
            document.getElementById("cmsg-btn-down").style.display = "none";
            document.getElementById("cmsg-btn-up").style.display = "none";
            document.getElementById("cmsg").innerHTML = "";
        }

    }
}

const main = () => {

// main function so that the page is fully loaded

document.getElementById("sselection-form-btn").onclick = (e) => {

    e.preventDefault();

    SERVER_ID = document.getElementById("sselection-form-list").value
    console.log("working with server of id ", SERVER_ID);

    // load server JSON
    read_local_JSON("../" + SERVER_ID +"/core.json")
        .then(data => {
            console.log(data);
            Object.freeze(data);

            // server info
            show_server(data);
            
            // channel selection
            const channel_options_HTML = data.channels.map( chn => {
                return "<option value=\"" + chn.id + "\">" + chn.name + "</option>"
            })
            .reduce((total, elem) => {
                return total + elem;
            });

            document.getElementById("cselection-form-list").innerHTML = channel_options_HTML;

            document.getElementById("cselection-form-btn").onclick = gen_channel_selector(data, false);
            document.getElementById("fselection-form-btn").onclick = gen_channel_selector(data, true);
        });
    }

};
