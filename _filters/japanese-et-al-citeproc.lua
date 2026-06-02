local function has_japanese(text)
  for _, codepoint in utf8.codes(text) do
    if (codepoint >= 0x3040 and codepoint <= 0x30ff)
        or (codepoint >= 0x3400 and codepoint <= 0x9fff)
        or (codepoint >= 0xf900 and codepoint <= 0xfaff) then
      return true
    end
  end
  return false
end

local function is_space(inline)
  return inline and (inline.t == "Space" or inline.t == "SoftBreak")
end

local function rewrite_author(author, al)
  local suffix = al:match("^al%.(.*)$")
  if suffix == nil then
    return nil
  end

  local trimmed = author
  local had_sentence_punct = false

  if trimmed:match("%.,$") then
    trimmed = trimmed:gsub("%.,$", "")
    had_sentence_punct = true
  elseif trimmed:match(",$") then
    trimmed = trimmed:gsub(",$", "")
  elseif trimmed:match("%.$") then
    trimmed = trimmed:gsub("%.$", "")
    had_sentence_punct = true
  end

  if not has_japanese(trimmed) then
    return nil
  end

  if had_sentence_punct and suffix == "" then
    suffix = "."
  end

  return trimmed .. "ら" .. suffix
end

local function fix_inlines(inlines)
  local fixed = pandoc.List()
  local i = 1

  while i <= #inlines do
    local author = inlines[i]
    local et = inlines[i + 2]
    local al = inlines[i + 4]

    if author and author.t == "Str"
        and is_space(inlines[i + 1])
        and et and et.t == "Str" and et.text == "et"
        and is_space(inlines[i + 3])
        and al and al.t == "Str" then
      local rewritten = rewrite_author(author.text, al.text)
      if rewritten then
        fixed:insert(pandoc.Str(rewritten))
        i = i + 5
      else
        fixed:insert(inlines[i])
        i = i + 1
      end
    else
      fixed:insert(inlines[i])
      i = i + 1
    end
  end

  return fixed
end

function Pandoc(doc)
  doc = pandoc.utils.citeproc(doc)
  return doc:walk({ Inlines = fix_inlines })
end
