# Offline Survey Sync – API Automation & Testing

## Part 1: Hands-On Technical Inspection & Automation

### Scenario A: The Offline Sync & Data Collision (API & Mobile)

**Question 2 – Strategy:**
Explain how you would test the Android app's background sync behavior under poor network conditions, such as the network dropping at 99% of a photo upload. What tools would you use and how?

### Answer

I would test the sync process under different network conditions and verify that data is not lost or duplicated.

I would cover:

* Stable network
* Slow network
* Intermittent network
* Network disconnected before sync starts
* Network disconnected during upload
* Network disconnected when a photo is almost completely uploaded
* Network restored after failure
* App moved to background during sync
* App restarted after an interrupted sync

For each case, I would check that:

* Survey data is not lost.
* Duplicate records are not created.
* Failed sync remains pending or is retried.
* The app does not show a successful sync when the upload actually failed.
* Data is synchronized correctly after the network is restored.

### Testing Failure at 99% Photo Upload

For the 99% upload case, I would:

1. Create a survey and attach a photo.
2. Start the background sync.
3. Monitor the photo upload request.
4. Interrupt the network when the upload is almost complete.
5. Check the app's sync status.
6. Verify that the local survey and photo information are still available.
7. Restore the network.
8. Allow the app to retry the sync.
9. Verify that the upload completes successfully.
10. Check that only one record exists on the server.

The failed upload should not be treated as a successful sync, and retrying should not create a duplicate record.

### Charles Proxy

I would use Charles Proxy to monitor the API traffic between the Android app and the backend.

I would use it to:

* Identify the survey/photo upload request.
* Inspect request and response data.
* Introduce network delay.
* Throttle the network.
* Interrupt or block a request.
* Check how the app handles a failed request.
* Verify retry behavior.

For the 99% scenario, I would monitor the upload request and interrupt the network when the upload is nearly complete. I would then check whether the app keeps the data pending and retries it after the network is restored.

### ADB

I would use ADB to monitor the device and application during the test.

```bash
adb devices
```

To verify that the device is connected.

```bash
adb shell dumpsys battery
```

To check the device/battery state.

```bash
adb shell dumpsys connectivity
```

To check connectivity information.

```bash
adb logcat
```

To monitor application logs during the sync.

I would look for events such as:

```text
Sync started
Photo upload started
Upload failed
Retry scheduled
Network restored
Retry started
Sync completed
```

I would also use ADB to test app backgrounding, foregrounding and restart scenarios.

### Expected Result

The application should handle temporary network failures without losing or duplicating data. A failed photo upload should remain recoverable, and synchronization should complete successfully after the network is restored.

---

### Scenario B: Dynamic Form Rendering & Regression (Web & Mobile)

### Regression Strategy for JSON-Driven Dynamic Screens

**Question:**
How do you design a regression test suite for an app where screens are generated dynamically from JSON? What would you automate and what would you leave for manual exploratory testing?

### Answer

Since the mobile screens are generated from JSON, I would make the regression suite data-driven instead of creating separate tests for every form.

The basic flow would be:

```text
JSON Schema
    ↓
Schema Validation
    ↓
Dynamic Screen Rendering
    ↓
Input Validation
    ↓
Visibility / Skip Logic
    ↓
Repeating Roster
    ↓
Save / Resume
```

I would keep different JSON schemas as test data, including simple forms, different input types, conditional questions, repeating rosters and previously released forms.

### What I Would Automate

I would automate stable and repetitive functionality that needs to be checked on every release.

**Schema validation**

* Required schema fields
* Unique question IDs
* Supported input types
* Valid options
* Valid visibility/skip logic references
* Invalid or incomplete schema handling

**Dynamic rendering**

I would verify that the correct UI component is created for each input type.

For example:

```text
inputType = Text
        ↓
Text field should be displayed
```

and:

```text
inputType = Dropdown
        ↓
Dropdown should be displayed
```

**Skip / Visibility Logic**

This would be one of the main areas for automation.

For example:

```text
Do you have a hobby? = Yes
        ↓
What is your hobby? → Visible
```

and:

```text
Do you have a hobby? = No
        ↓
What is your hobby? → Hidden
```

I would cover both positive and negative conditions.

**Validation**

I would automate:

* Required and optional fields
* Valid and invalid input
* Boundary values
* Dropdown options
* Validation messages
* Form submission

**Repeating Rosters**

I would automate important cases such as:

* Add a member
* Remove a member
* Generate questions for each member
* Verify one member's data does not overwrite another member's data
* Save and reopen the roster

**Backward Compatibility**

I would keep previously released JSON schemas as regression data and run them against the current rendering logic whenever the Survey Builder is changed.

### What I Would Keep for Manual Exploratory Testing

I would use manual testing for areas where human observation is important.

This would include:

* UI layout and alignment
* Text overlap or truncation
* Touch and keyboard behavior
* Scrolling
* Different screen sizes
* Screen orientation
* Usability
* Accessibility
* Unexpected combinations of conditional questions
* Large or complex forms
* Real-device behavior
* App background/foreground and restart scenarios

### Automation vs Manual

| Area                       | Automation | Manual |
| -------------------------- | :--------: | :----: |
| JSON schema validation     |     Yes    |        |
| Input type rendering       |     Yes    |        |
| Skip / visibility logic    |     Yes    |        |
| Required field validation  |     Yes    |        |
| Form validation            |     Yes    |        |
| Repeating roster core flow |     Yes    |        |
| Backward compatibility     |     Yes    |        |
| Data persistence           |     Yes    |        |
| UI layout / usability      |            |   Yes  |
| Touch / keyboard behavior  |            |   Yes  |
| Different physical devices |  Partially |   Yes  |
| Unexpected user flows      |            |   Yes  |
| Accessibility exploration  |  Partially |   Yes  |

I would run a small smoke suite on every build, functional regression when related features change, and a wider regression before release.

---

### Scenario C: Offline Sync & State Management (Android WorkManager & Room)

### Technical Inspection Strategy

**Question:**
Imagine you are provided with the release APK. Explain how you would inspect the Room database, force the WorkManager job, simulate a 500 response and verify retry without losing local data.

### Answer

I would test this in three stages: before sync, during the failed sync, and after retry.

### 1. Inspecting the Room Database

First, I would disable the network and create a survey from the app.

I would identify the package name using:

```bash
adb shell pm list packages
```

For a debuggable/test build, I would check the database using:

```bash
adb shell run-as <package_name> ls databases
```

I would then copy the database for inspection and open it using Android Studio Database Inspector or an SQLite viewer.

I would verify:

* Survey/local ID
* Survey answers
* Sync status
* Created/updated time
* Local sync ID
* Photo/file reference, if applicable

For a real non-debuggable release APK on an unrooted device, direct access to the private application database is normally restricted. In that case, I would use an approved debug/test build or an application-provided database export/debug mechanism.

### 2. Force the WorkManager Sync

I would first check the scheduled jobs:

```bash
adb shell dumpsys jobscheduler
```

I would identify the job belonging to the application and note its Job ID.

Then I would trigger the job:

```bash
adb shell cmd jobscheduler run -f <package_name> <job_id>
```

I would monitor the application logs:

```bash
adb logcat
```

I would verify that the sync worker starts and attempts to send the locally stored survey.

### 3. Simulate a 500 Response

I would configure Charles Proxy between the Android device and the test backend.

I would:

1. Start the survey sync.
2. Find the sync API request in Charles.
3. Intercept the response.
4. Return HTTP `500 Internal Server Error`.
5. Allow the response to reach the application.
6. Check how the app handles the failure.

### 4. Verify Retry Without Data Loss

After the 500 response, I would verify that:

* The local Room record still exists.
* Survey answers have not changed or been lost.
* The survey is still pending/unsynchronized.
* The failed request is not treated as successful.
* A retry is scheduled.
* The app does not create a duplicate local record.

I would then remove the failure condition in Charles and allow the next retry to reach the server.

After successful retry, I would verify:

* Server contains the survey.
* Local status changes to synced.
* Original survey data is unchanged.
* No duplicate server record is created.

This verifies the complete flow from offline storage to failed sync, retry and successful synchronization.

---

## Part 2: Complex Scenarios & Edge Cases

### Scenario D: The Edge-Case Device Constraints

**Question:**
Walk through how you would reproduce this issue, debug it and prove the root cause to a developer. What ADB commands, profilers or device techniques would you use to simulate low storage and memory limits?

### Answer

First, I would reproduce the issue on a 4 GB RAM device using the same offline video sequence. I would also repeat the test on a high-end device so I can compare the behavior.

I would check the device resources using:

```bash
adb shell free -m
adb shell df -h
adb shell getprop ro.product.model
```

I would clear the app data and start from a clean state:

```bash
adb shell pm clear <package_name>
```

Then I would watch the 3–4 offline training videos and note exactly when the problem starts.

For memory usage, I would use:

```bash
adb shell dumpsys meminfo <package_name>
```

I would also use Android Studio Profiler to check whether memory keeps increasing after each video and whether it is released when the video is closed.

To simulate low storage, I can create a temporary file on the test device:

```bash
adb shell dd if=/dev/zero of=/sdcard/testfile.bin bs=1M count=1000
```

Then I would check the available storage again using:

```bash
adb shell df -h
```

When the issue occurs, I would collect logs:

```bash
adb logcat -c
adb logcat > anr_log.txt
```

For an ANR, I would also check:

```bash
adb shell dumpsys activity anr
```

I would compare the memory usage, storage and logs from the 4 GB device with the high-end device.

If the memory keeps increasing after each video and the app becomes unresponsive when memory pressure is high, I would provide the profiler data, logs, device details and exact reproduction steps to the developer.

I would not call it a memory leak unless the collected evidence supports that conclusion.

---

### Scenario E: The HFC (High-Frequency Checks) Engine

**Question:**
Design a brief test plan for testing the HFC engine itself. Include positive, negative and edge-case scenarios to ensure it blocks invalid data when necessary but does not trap a user in an infinite loop.

### Answer

I would test each HFC rule with positive, negative, boundary and repeated inputs.

| Test Case | Condition                            | Test Data                      | Expected Result                                                                                    | Type     |
| --------- | ------------------------------------ | ------------------------------ | -------------------------------------------------------------------------------------------------- | -------- |
| HFC-001   | Age < 15 AND Education = College     | Age: 14, Education: College    | `reask_and_flag` should trigger                                                                    | Positive |
| HFC-002   | Age < 15 AND Education = College     | Age: 15, Education: College    | HFC should not trigger                                                                             | Edge     |
| HFC-003   | Age < 15 AND Education = College     | Age: 14, Education: School     | HFC should not trigger                                                                             | Negative |
| HFC-004   | Age < 15 AND Education = College     | Age: 20, Education: College    | HFC should not trigger                                                                             | Negative |
| HFC-005   | Sleep Well = Yes AND Sleep hours < 6 | Yes, 5 hours                   | `reask_and_flag` should trigger                                                                    | Positive |
| HFC-006   | Sleep Well = Yes AND Sleep hours < 6 | Yes, 6 hours                   | HFC should not trigger                                                                             | Edge     |
| HFC-007   | Sleep Well = Yes AND Sleep hours < 6 | No, 5 hours                    | HFC should not trigger                                                                             | Negative |
| HFC-008   | Missing value in condition           | Age: Blank, Education: College | Input should be handled correctly without an incorrect HFC trigger                                 | Edge     |
| HFC-009   | Invalid input                        | Age: -1, Education: College    | Invalid age should be rejected/validated                                                           | Edge     |
| HFC-010   | Same invalid data entered repeatedly | Age: 14, Education: College    | System should stop after the configured retry limit and flag the record instead of looping forever | Edge     |

The main checks are:

* HFC triggers when all required conditions are satisfied.
* HFC does not trigger when the conditions are not satisfied.
* Boundary values such as `Age = 15` and `Sleep hours = 6` are handled correctly.
* Missing or invalid values do not cause unexpected behavior.
* Repeated invalid answers do not keep the user in an infinite re-ask loop.

---

## Part 3: QA Process & AI Integration

### 1. Process Creation

**Question:**
You are joining as the first dedicated QA Engineer. Developers currently test their own code and push directly to the Play Store. Walk through your first 30 days. How would you introduce a structured QA process without slowing down the development team?

### Answer

In the first 30 days, I would first understand the current development and release process before making major changes.

**Week 1 – Understand the current process**

I would understand how features are developed, tested and released. I would also look at existing test coverage, production issues and the type of bugs developers usually find after release.

**Week 2 – Introduce a basic QA flow**

I would introduce a simple flow:

```text
Development → QA/Staging Build → Testing → Bug Fix → Retesting → Release
```

I would also define basic entry and exit criteria.

**Entry criteria:**

* Feature is completed and available in the QA build.
* Developer testing is completed.
* Basic smoke checks are passing.

**Exit criteria:**

* Planned testing is completed.
* No open critical/blocker bugs.
* Important regression cases are passing.
* Known issues are documented.

**Week 3 – Regression and release checks**

I would create a small smoke and regression suite for important areas such as survey creation, offline saving and sync.

I would not try to automate everything immediately. I would first automate stable and repetitive scenarios.

I would also recommend using a staging/test build instead of sending every change directly to the Play Store.

**Week 4 – Improve and automate**

Once the basic process is working, I would start adding automation and CI checks for stable regression cases.

I would keep the process lightweight. For small changes, I would use risk-based testing, while bigger or high-risk changes would get more detailed testing.

The main goal would be to catch important issues before release without creating unnecessary delays for developers.

### 2. Leveraging AI

**Question:**
How do you currently use AI tools in your day-to-day QA workflow? Give a specific example of how AI could help you write tests for the complex dynamic schemas mentioned in Scenario B.

### Answer

I use AI mainly as a support tool during testing and automation. I don't use it as a replacement for my own testing.

For example, I can use ChatGPT to:

* Find additional test scenarios and edge cases.
* Understand a complex JSON structure.
* Create test data.
* Review test cases.
* Get suggestions when writing Selenium/Pytest code.
* Understand an error when I am stuck.
* Improve or simplify automation code.

For Scenario B, I could provide the JSON containing the question and its visibility logic.

For example:

```text
Do you have a hobby? = Yes
        ↓
What is your hobby? = Visible
```

I could ask AI to suggest positive, negative and boundary scenarios around this rule.

It may suggest:

* Select Yes → field should be visible.
* Select No → field should be hidden.
* Change Yes to No → field should become hidden.
* Change No to Yes → field should become visible.
* Do not select an answer → check the default behavior.

I can then use these scenarios while writing the Selenium/Pytest tests.

I would still review the suggested test cases and code myself because the final test should be based on the actual requirement and application behavior.

### 3. Automation Tooling

**Question:**
With limited time, how do you decide what should be automated versus what should not be automated? Why did you choose the specific tools used for Part 1?

### Answer

I normally look at how often a test is executed, how stable the feature is and how much manual effort the test takes.

I would automate:

* Repetitive regression tests
* Smoke tests
* API validations
* Stable business flows
* Data validation
* Scenarios with many input combinations

I would keep manual testing for:

* Exploratory testing
* New or frequently changing features
* Usability and UI checks
* Visual issues
* One-time or low-value scenarios

For this assignment, I used **Postman** for the API testing because it was quick to create the sync requests, validate responses and test duplicate/idempotency behavior.

For the web automation, I used **Python, Selenium and Pytest** because I already have experience with these tools and they were enough for the dynamic visibility test required in the assignment.

I prefer starting with a small set of useful automation tests and then expanding it based on the application's needs.

---

## Part 4: UI/UX & User-Centric QA

### 1. Scenario Evaluation

**Question:**
A developer submits a new "Training Video Hub" screen for QA. It has a standard video player, 3 paragraphs describing the video, and a standard-sized "Next" button at the bottom of a scrollable page. How would you evaluate this screen beyond basic functional testing?

### Answer

I would not only check whether the video plays and the Next button works. I would also check whether a field worker can use the screen easily on a small and low-end phone.

I would test it on a budget Android device and, if possible, in conditions similar to the actual field environment.

I would check:

* Is the text easy to read?
* Is there too much information on one screen?
* Can the text and buttons be seen clearly in bright sunlight?
* Is the Next button easy to tap?
* Are the video controls easy to use?
* Is scrolling smooth on a low-end device?
* Does the layout look correct on a small screen?
* Does the app remain responsive while the video is playing?

### 2. UX/UI Issues and Rendering Risks

Based on the target users, I would specifically look for:

| Issue                          | Risk                                                                      |
| ------------------------------ | ------------------------------------------------------------------------- |
| Text is too small              | Users may have difficulty reading it.                                     |
| Three long paragraphs          | The screen may feel too text-heavy for users with limited reading skills. |
| Low contrast                   | Text and controls may be difficult to see in bright sunlight.             |
| Small Next button              | It may be difficult to tap correctly on a small screen.                   |
| Next button only at the bottom | The user has to scroll all the way down before continuing.                |
| Small video controls           | Play, pause and other controls may be difficult to tap.                   |
| Icons are not clear            | Users may not understand an icon without a clear visual cue or label.     |
| Layout on small screens        | Text, buttons or video controls may overlap or get cut off.               |
| Slow performance               | Video playback or scrolling may lag on a budget device.                   |

### 3. How I Would Test These Issues

I would test the screen using real devices and normal QA checks.

**Device testing**

I would use a low-end Android phone with a smaller screen and compare the same screen with a higher-end device.

**Readability and visibility**

I would check font size, spacing and contrast. I would also check the screen in normal indoor light and bright light.

**Touch**

I would check whether the Next button and video controls are easy to tap. I would also check for accidental taps while scrolling.

**Navigation**

I would check whether the user can easily understand what to do next and whether too much scrolling is required.

**Video**

I would check play, pause, seeking, full screen, loading and resume behavior. If the video depends on the network, I would also test it with a slow or unstable connection.

**Performance**

On the low-end device, I would check for lag, freezing, slow response, high memory usage, crashes or ANR while playing the video and scrolling.

### 4. How I Would Report Non-Functional Bugs

For UX issues, I would give the developer and designer clear information instead of simply saying that the UI is not good.

For example:

**Issue:** Next button is difficult to tap on a small-screen device.

**Device:** Low-end Android device with a small display.

**Steps:**

1. Open the Training Video Hub.
2. Play the video.
3. Scroll to the bottom.
4. Try tapping the Next button.

**Actual Result:**
The button is small and requires precise tapping.

**Impact:**
A field worker may miss the button or tap the wrong area, making it difficult to continue.

**Recommendation:**
Increase the touch area of the button and keep enough space around it.

I would attach a screenshot or short recording when needed and discuss the issue with the developer/designer based on the actual user impact and device evidence.
