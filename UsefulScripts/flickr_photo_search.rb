#! /usr/bin/ruby -w
# flickr_photo_search.rb
# @author:Marc Steven
# date:2019-9-5

require 'open-uri'
require 'rexml/document'

# Returns the URI to a small version of a flickr photo
def small_photo_url(photo)
  server = photo.attribute('server')
  id = photo.attribute('id')
  secret = photo.attribute('secret')
  return  "http://static.flickr.com/#{server}/#{id}_#{secret}_m.jpg"
end
def  print_each_photo(api_key,tag)
  uri = "http://www.flickr.com/services/rest?method=flickr.photos.search"+ "$api_key = #{api_key}&tags = #{tag}"

  response = open(uri).read
  doc = REXML::Document.new(response)
  REXML:: XPath.each(doc,'//photo') do |photo|
    put small_photo_url(photo) if  photo
  end
end

if  ARGV.size < 2
  puts "Usage:#{$0} [Flickr API key] [search term]"
  exit
end
api_key,tag = ARGV
print_each_photo(api_key,tag)