+++
date = '{{ .Date }}'
draft = false
title = '{{ replace .File.ContentBaseName "_" " " | title }}'
type = "wiki"
wiki_slug = '{{ .File.ContentBaseName }}'
+++
