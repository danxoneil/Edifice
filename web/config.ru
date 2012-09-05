require 'bundler'
Bundler.require :default

base = File.dirname(__FILE__)   # finds dir this file is in
$:.unshift File.join(base, "lib")   # adds "lib" to base project dir to build path that points to where edifice sinatra app lives, and adds this path to the ruby path.  

require 'edifice'

Sinatra::Base.set(:root) { base }
run Edifice::Application

