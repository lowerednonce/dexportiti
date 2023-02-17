#!/usr/bin/python3
import json
import sys

def main(location: str):
    with open("../" + location + "/core.json", "r") as f:
        parsed = json.loads(f.read())
        for chn_i in range(len(parsed["channels"])):
            print(parsed["channels"][chn_i]["name"])
            if(parsed["channels"][chn_i]["type"] != "text"):
                print("non-text type for " + parsed["channels"][chn_i]["name"])
                continue
            for msg_i in range(len(parsed["channels"][chn_i]["messages"])):
                parsed["channels"][chn_i]["messages"][msg_i]["author"] = str(parsed["channels"][chn_i]["messages"][msg_i]["author"]) 
                parsed["channels"][chn_i]["messages"][msg_i]["id"]     = str(parsed["channels"][chn_i]["messages"][msg_i]["id"]) 
                for a_i in range(len(parsed["channels"][chn_i]["messages"][msg_i]["attachments"])):
                    print(f'converting {parsed["channels"][chn_i]["messages"][msg_i]["attachments"][a_i]["id"]} to str')
                    parsed["channels"][chn_i]["messages"][msg_i]["attachments"][a_i]["id"] = str(parsed["channels"][chn_i]["messages"][msg_i]["attachments"][a_i]["id"])
                                     # ugly AF but idc
        for user_i in range(len(parsed["members"])):
            parsed["members"][user_i]["id"] = str(parsed["members"][user_i]["id"])

    with open("../" + location + "/core.json", "w") as f:
        json.dump(parsed, f)
    with open("../" + location + "/core-pretty.json", "w") as f:
        json.dump(parsed, f, indent=4)



if __name__ == "__main__":
    if(len(sys.argv) < 2):
        print("Error, please provide server id to fix")
        exit(-1)
    main(sys.argv[1])
