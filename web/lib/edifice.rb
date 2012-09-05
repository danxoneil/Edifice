require 'sinatra'
require 'sinatra-initializers'

module Edifice
    class Application < Sinatra::Base

        get '/' do
           'Hello, World!'
        end
        
    end
end
