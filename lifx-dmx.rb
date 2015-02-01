require 'lifx'
require 'base64'

client = LIFX::Client.lan
client.discover!
l = client.lights.lights[0]

m = Mutex.new

# Setting the colour is a bit slow; we can't keep up with all the messages
# Artemis sends. So we set the colour in a separate thread, only if no such
# thread is already running

while true do
    s = gets
    d = Base64.decode64(s)
    if d[0] == "\x00" then
        c = LIFX::Color.rgb(d[1].ord, d[2].ord, d[3].ord)
        t = Thread.new {
            if m.try_lock then
                l.set_color(c, duration: 0)
                puts "Successfully set color to #{d[1].ord} #{d[2].ord} #{d[3].ord}"
                sleep 0.25
                m.unlock
            end
        }
    end
end
