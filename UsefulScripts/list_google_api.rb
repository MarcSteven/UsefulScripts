#! /usr/bin/ruby

#Created by Marc Steven(https://medium.com/@MarcStevenCoder) in 2017/10/21 


require 'rubygems'
require 'net/https'
require 'json'

url = 'https://www.googleapis.com/discovery/v1/apis'
uri = URI.parse(url)


#set up a connetction to the Google API Service
http = Net::HTTP.new(uri.host,443)
http.use_ssl = true
http.verify_mode = OpenSSL::SSL::VERIFY_NONE

#connect to the service
req = Net::HTTP::Get.new(uri.request_uri)
response = http.request(req)
#ItERATE THROUGH THE API LIST
jresp['item'].each do |item |
  if item['preferred'] = true
  name = item['name']
  title = item['title']
  link = item['discoveryLink']
  printf("%-17s %- 34s %- 20s\n",name,title,link)
end
end
