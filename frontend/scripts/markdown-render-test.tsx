import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import assert from "node:assert/strict";
import MarkdownViewer from "../src/components/MarkdownViewer";

const render = (content: string) =>
  renderToStaticMarkup(<MarkdownViewer content={content} />);

const plain = render("```\nint value = 42;\n```");
assert.match(plain, /code-block-wrapper/, "Unlabeled fences need the code block UI");
assert.match(plain, /复制代码/, "Unlabeled code should be copyable");

const labeled = render("```c++\nint value = 42;\n```");
assert.match(labeled, />c\+\+</, "Preserve punctuation in language names");
assert.doesNotMatch(labeled, /<pre[^>]*><div/, "Block UI must not be inside pre");
assert.equal((labeled.match(/<pre[\s>]/g) || []).length, 1);

const inline = render("Use `int value` here.");
assert.match(inline, /class="inline-code"/, "Inline code keeps inline styling");
assert.doesNotMatch(inline, /code-block-wrapper/);

const steps = render("3. Third step\n4. Fourth step");
assert.match(steps, /<ol[^>]*start="3"/, "Retain ordered list starting number");
console.log("Markdown rendering regressions: 4 scenarios passed");
