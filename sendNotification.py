import http.client, urllib
token = ""
user = ""

def sendNotification(): 
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": token,
        "user": user,
        "message": "FOUND",
    }), { "Content-type": "application/x-www-form-urlencoded" })
    response = conn.getresponse()
    print (response.status)
    print (response.read())