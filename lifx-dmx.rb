require 'lifx'
require 'base64'
require 'json'

TAGS = JSON.load(open('tags.json')).map{ |i| i[0] }

client = LIFX::Client.lan
client.discover!
l = client.lights.lights[0]

red_alert = false

def decode_packet(s)
    d = Base64.decode64(s)
    Hash[TAGS.each_with_index.map{ |a, i| [a, (d[i + 1] != "\x00")] }]
end

while true do
    s = gets
    d = decode_packet(s)
    puts d
    if d['RED_ALERT'] then
        if not red_alert then
            red_alert = true
            l.set_color(LIFX::Color.red, duration: 0)
        end
    else
        if red_alert then
            red_alert = false
            l.set_color(LIFX::Color.white, duration: 0)
        end
    end
end
