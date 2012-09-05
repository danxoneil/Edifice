require 'sinatra'

module Edifice
    class Application < Sinatra::Base

        get '/' do
           haml :index
       end
        
    end
end
