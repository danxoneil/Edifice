require 'sinatra'

module Edifice
    class Application < Sinatra::Base

       get '/' do
           haml :index
       end

       get '/leaflet' do
           haml :leaflet
       end
        
    end
end
