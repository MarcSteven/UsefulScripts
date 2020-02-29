#
# Use this script to convert all the views on a Rails app from ERB to HAML
#

files = Dir['**/*.html.erb']

files.each do |f|
  base = f.split('.')[0..-2].join(".")
  output = base + '.haml'

  %x{html2haml #{f} #{output}}
  %x{rm #{f}}
end
