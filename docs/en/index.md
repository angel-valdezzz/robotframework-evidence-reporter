---
hide:
  - toc
---

<div class="hero" markdown>
<div class="project-brand">
<img class="project-brand-light" src="assets/logo-wordmark.svg" alt="Evidence Reporter">
<img class="project-brand-dark" src="assets/logo-wordmark-dark.svg" alt="Evidence Reporter">
</div>

<span class="eyebrow">Robot Framework · Business evidence</span>

# What you tested, ready to share

**One report per case**, with execution results, screenshots, milestones and messages explaining what happened without getting lost in every click's technical details.

[Get started](getting-started.md){ .md-button .md-button--primary }
[Visual examples](demo/passed.html){ .md-button }
</div>

<div class="grid cards" markdown>

-   :material-camera-outline:{ .card-icon } **Capture what matters**

    ---

    Visible page, element or desktop. Choose when to record evidence and how to describe it.

    [Choose a capture →](keywords.md)

-   :material-view-dashboard-outline:{ .card-icon } **Read the case result**

    ---

    Summary, Steps and Logs. Collapsible milestones, light/dark themes and expandable images.

    [Explore the demo →](demo.md)

-   :material-file-code-outline:{ .card-icon } **Generate after execution**

    ---

    Robot records JSON and images; CLI or Python converts them into standalone reports.

    [Generate reports →](generation.md)

-   :material-call-split:{ .card-icon } **Run in parallel**

    ---

    Independent case directories support Pabot without overwriting evidence.

    [Configure Pabot →](parallel.md)

</div>

## From business flow to report

1. **Execute** a case with Robot or Pabot.
2. **Record** captures and messages using explicit keywords.
3. **Generate** an individual report and share the file.

!!! info "Two independent results"
    **Execution status** comes from Robot. **Evidence status** describes a capture. Recording an error with `status=FAIL` does not itself change the test result.

## Report preview

[![Case summary in light mode](assets/images/report-light.png){ .report-preview }](demo/passed.html)

The image illustrates a demo with fictitious data. Open the report to change themes, inspect milestones and enlarge evidence images. The demo's interface remains Spanish.
