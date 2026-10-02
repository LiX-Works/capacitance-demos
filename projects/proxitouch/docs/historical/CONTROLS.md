# 操作说明 / Controls

The presentation is a slide-like sequence of 23 knowledge units. A page's internal keyframes are one continuous causal animation, not compulsory click-by-click beats.

|Control|Action|
|---|---|
|Right / Space / Page Down / Next button|During animation, immediately finish this page. A second press advances to the next page and starts its animation.|
|Left / Page Up / Previous button|Previous page at its stable ending state.|
|R|Replay the current page. In Explore, reset camera and interaction depth to -0.4.|
|T / 原理说明|Collapse or expand the default-visible body. Scroll it independently with the wheel.|
|G / 目录|Open the 23-page chapter index; selecting a page starts its animation.|
|E / 探索|Enter or leave Explore; preserve presentation state and body scroll.|
|Esc|Close dialogs; leave Explore when active.|
|P|Start or stop full-sequence autoplay. Stopping autoplay does not rewind the current animation.|
|Home / End|Cover / final stable scene.|
|关于|Conceptual-model limitations and keyboard guide.|

## Explore

|Control|View / action|
|---|---|
|V|Device: shared EC in the new EH-EC-EB geometry.|
|F|Field: generic mutual field in Part I; new EH-EC device field in design pages.|
|M|Microstructure: flexible EC, air gap, domes and effective contact area.|
|N|Nano / EDL: stable lower interface; upper interface follows contact state.|
|S|HC / CB normalized signals, derived from the same interaction state.|
|X|Exploded layer view; separated layers are a structural illustration, not working gaps.|
|Drag on model|Orbit camera.|
|Wheel on model|Zoom camera.|
|Depth slider|Move from far to contact to pressure. This is a normalized teaching coordinate.|
|A / 自动交互|Run or pause an 11-second smooth exploratory interaction cycle.|
|Quality selector|High, medium, or SAFE. SAFE lowers render resolution and shading cost, not scene coverage.|

Keyboard navigation ignores repeated keydown events. Arrow keys while a slider/select is focused control that native input; leaving Explore explicitly returns focus to the canvas so global navigation works again. Text scrolling does not rotate or zoom the model. Presentation mode does not depend on dragging the camera.

## R3 ambient animations

S05 material emphasis, S07 coupling indicators, S10 final upper-interface breathing and S18 multiplex windows use a separate active-scene clock. They never set the main animation to playing. Once the main animation ends, Next advances even while these loops are running. Entering Explore pauses the presentation clock; leaving restores the saved presentation state. Leaving the page stops that page's updates. R restarts the main animation and ambient time.

Capture API: `__PT.captureMode(true); __PT.goTo('S18', 1); __PT.ambientTime(1.5); __PT.flush();` fixes the CB window. Use `__PT.captureMode(false)` for real-time playback.
