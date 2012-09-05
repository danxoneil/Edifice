require 'sinatra'

module Edifice
    class Application < Sinatra::Base

        get '/' do
            puts 'Hello, World!'
        end
        
    end
end
