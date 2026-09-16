# frozen_string_literal: true

# Chrome stalls HTML5 video on `jekyll serve` because WEBrick FileHandler
# raises PartialContent for Range requests before Jekyll merges webrick.headers.

require "webrick"
require "jekyll/commands/serve/servlet"

module JekyllWebrickVideoHeaders
  def do_GET(req, res)
    apply_webrick_headers!(res)
    super
  rescue WEBrick::HTTPStatus::PartialContent, WEBrick::HTTPStatus::NotModified
    apply_webrick_headers!(res)
    raise
  end

  def apply_webrick_headers!(res)
    res.header.merge!(@headers) if defined?(@headers) && @headers
  end
end

Jekyll::Commands::Serve::Servlet.prepend(JekyllWebrickVideoHeaders)
