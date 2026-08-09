local function escape_html(value)
  return tostring(value or "")
    :gsub("&", "&amp;")
    :gsub("<", "&lt;")
    :gsub(">", "&gt;")
    :gsub('"', "&quot;")
    :gsub("'", "&#39;")
end

local difficulty_levels = {
  A = 1,
  B = 2,
  C = 3,
  D = 4,
}

local difficulty_names = {
  A = "取り組みやすい",
  B = "標準",
  C = "発展",
  D = "挑戦",
}

local function difficulty_meter(level)
  local segments = {}
  for index = 1, 4 do
    local state = index <= level and " is-active" or ""
    table.insert(segments, '<span class="exercise-meta-card__segment' .. state .. '"></span>')
  end
  return table.concat(segments)
end

function Div(element)
  if not element.classes:includes("exercise-meta") then
    return nil
  end

  local difficulty = element.attributes.difficulty or "-"
  local expected_time = element.attributes.time or "-"
  local rank = difficulty:match("^([ABCD])") or "B"
  local level = difficulty_levels[rank]
  local name = difficulty_names[rank]

  if not FORMAT:match("html") then
    return pandoc.Div({
      pandoc.Para({
        pandoc.Strong("難易度 " .. difficulty),
        pandoc.Space(),
        pandoc.Str("／ 目安 " .. expected_time),
      }),
    })
  end

  local html = string.format([[
<dl class="exercise-meta-card exercise-meta-card--%s" aria-label="演習情報">
  <div class="exercise-meta-card__item">
    <dt><span class="exercise-meta-card__icon" aria-hidden="true">◇</span>難易度</dt>
    <dd>
      <strong>%s</strong>
      <span class="exercise-meta-card__meter" aria-hidden="true">%s</span>
      <span class="visually-hidden">%s、4段階中%d</span>
    </dd>
  </div>
  <div class="exercise-meta-card__item">
    <dt><span class="exercise-meta-card__icon" aria-hidden="true">◷</span>所要時間</dt>
    <dd><strong>%s</strong><span class="exercise-meta-card__hint">目安</span></dd>
  </div>
</dl>
]], rank, escape_html(difficulty), difficulty_meter(level), name, level, escape_html(expected_time))

  return pandoc.RawBlock("html", html)
end
