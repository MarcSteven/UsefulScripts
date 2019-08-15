#! usr/bin/ruby -w
# redirect_stdout.rb
# Author:Marc Steven(https://www.medium.com/@MarcStevenCoder)
# Date:15/8/2019

require 'stringio'


new_stdout = StringIO.new

$stdout = new_stdout

puts "hello,hello"
put "I am writing a standard output"
$stderr.puts "#{new_stdout.size} bytes written to standard output so far"
$stderr.puts "U have not seen anything on the screen yet, but you soon will:"
$stderr.puts new_stdout.string
