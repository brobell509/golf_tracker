from bakery import assert_equal
from drafter import *
from dataclasses import dataclass


# Website information
set_website_title("Golf Score Tracker")

set_site_information(
    author="Your Actual Name",
    description="A website for recording golf scores and tracking performance.",
    sources="Drafter library and CISC106 course materials.",
    planning=["plan.pdf", "design.pdf"],
    links=["https://github.com/your-username/your-repository"]
)

hide_debug_information()
set_website_framed(False)


# Stores information about one completed golf round
@dataclass
class GolfRound:
    course_name: str
    scores: list[int]
    pars: list[int]
    total_score: int
    total_par: int
    score_to_par: int


# Stores information the website needs to remember
@dataclass
class State:
    golfer_name: str
    course_name: str
    current_scores: list[int]
    current_pars: list[int]
    rounds: list[GolfRound]
    selected_round_index: int
    message: str


def describe_score(score_to_par: int) -> str:
    """Describe the golfer's score compared with par."""
    if score_to_par > 0:
        return str(score_to_par) + " over par"
    elif score_to_par < 0:
        return str(abs(score_to_par)) + " under par"
    else:
        return "Even par"


def calculate_totals(scores: list[int],
                     pars: list[int]) -> tuple[int, int, int]:
    """Calculate total strokes, total par, and the difference."""
    total_score = 0
    total_par = 0

    for score in scores:
        total_score = total_score + score

    for par in pars:
        total_par = total_par + par

    score_to_par = total_score - total_par

    return total_score, total_par, score_to_par


def calculate_average_score(rounds: list[GolfRound]) -> float:
    """Calculate the average total score across completed rounds."""
    if len(rounds) == 0:
        return 0.0

    total_scores = 0

    for golf_round in rounds:
        total_scores = total_scores + golf_round.total_score

    return total_scores / len(rounds)


def make_hole_descriptions(scores: list[int],
                           pars: list[int]) -> list[str]:
    """Create descriptions of each hole's score."""
    descriptions = []

    for i in range(len(scores)):
        description = (
            "Hole " + str(i + 1) +
            ": " + str(scores[i]) +
            " strokes (Par " + str(pars[i]) + ")"
        )
        descriptions.append(description)

    return descriptions


# PAGE 1: Home page
@route
def index(state: State) -> Page:
    """Display the home page and main website options."""
    return Page(state, [
        Header("Golf Score Tracker"),
        "Welcome to the Golf Score Tracker!",
        "Enter your golf scores, calculate your results, and review previous rounds.",
        "Golfer: " + state.golfer_name,
        Button("Start a New Round", "start_round"),
        Button("View Round History", "history"),
        Button("How to Use", "help")
    ])


# PAGE 2: Start a round
@route
def start_round(state: State) -> Page:
    """Display the form for starting a new golf round."""
    return Page(state, [
        Header("Start a New Round"),
        "Enter your name and the golf course.",
        "Golfer Name:",
        TextBox("golfer_name", state.golfer_name),
        "Course Name:",
        TextBox("course_name", state.course_name),
        Button("Begin Round", "begin_round"),
        Button("Home", "index")
    ])


# ROUTE: Save the golfer and course information
@route
def begin_round(state: State, golfer_name: str,
                course_name: str) -> Page:
    """Save the golfer and course and prepare a new scorecard."""
    if golfer_name.strip() == "" or course_name.strip() == "":
        state.message = "Please enter both your name and the course name."
        return start_round(state)

    state.golfer_name = golfer_name.strip()
    state.course_name = course_name.strip()
    state.current_scores = []
    state.current_pars = []
    state.message = ""

    return scorecard(state)


# PAGE 3: Scorecard
@route
def scorecard(state: State) -> Page:
    """Display the current golf scores and hole-entry form."""
    content = [
        Header("Current Scorecard"),
        "Golfer: " + state.golfer_name,
        "Course: " + state.course_name
    ]

    if state.message != "":
        content.append(state.message)

    if len(state.current_scores) == 0:
        content.append("You have not entered any holes yet.")
    else:
        content.append("Your scores so far:")

        for description in make_hole_descriptions(
                state.current_scores, state.current_pars):
            content.append(description)

    content.append("Enter the number of strokes:")
    content.append(TextBox("strokes", 4, "number"))

    content.append("Choose the par for this hole:")
    content.append(SelectBox("par", ["3", "4", "5"], "4"))

    content.append(Button("Add Hole", "add_hole"))
    content.append(Button("Finish Round", "finish_round"))
    content.append(Button("Home", "index"))

    return Page(state, content)


# ROUTE: Add a hole to the current scorecard
@route
def add_hole(state: State, strokes: int, par: str) -> Page:
    """Check the hole information and add it to the scorecard."""
    if strokes <= 0:
        state.message = "Strokes must be greater than zero."
    elif par != "3" and par != "4" and par != "5":
        state.message = "Please choose a valid par."
    else:
        state.current_scores.append(strokes)
        state.current_pars.append(int(par))
        state.message = "Hole added successfully!"

    return scorecard(state)


# ROUTE: Finish the round and save it
@route
def finish_round(state: State) -> Page:
    """Calculate the round totals and save the completed round."""
    if len(state.current_scores) == 0:
        state.message = "Enter at least one hole before finishing."
        return scorecard(state)

    total_score, total_par, score_to_par = calculate_totals(
        state.current_scores, state.current_pars
    )

    completed_round = GolfRound(
        state.course_name,
        state.current_scores.copy(),
        state.current_pars.copy(),
        total_score,
        total_par,
        score_to_par
    )

    state.rounds.append(completed_round)
    state.selected_round_index = len(state.rounds) - 1

    state.current_scores = []
    state.current_pars = []
    state.message = "Your round has been saved!"

    return round_summary(state)


# PAGE 4: Completed round summary
@route
def round_summary(state: State) -> Page:
    """Display the results of the most recently selected round."""
    if (state.selected_round_index < 0 or
            state.selected_round_index >= len(state.rounds)):
        return history(state)

    golf_round = state.rounds[state.selected_round_index]

    content = [
        Header("Round Summary"),
        "Golfer: " + state.golfer_name,
        "Course: " + golf_round.course_name,
        "Total Strokes: " + str(golf_round.total_score),
        "Total Par: " + str(golf_round.total_par),
        "Result: " + describe_score(golf_round.score_to_par),
        "Hole-by-hole scores:"
    ]

    for description in make_hole_descriptions(
            golf_round.scores, golf_round.pars):
        content.append(description)

    content.append(Button("View Round History", "history"))
    content.append(Button("Start Another Round", "start_round"))
    content.append(Button("Home", "index"))

    return Page(state, content)


# PAGE 5: Round history
@route
def history(state: State) -> Page:
    """Display saved rounds and the golfer's average score."""
    content = [Header("Round History")]

    if len(state.rounds) == 0:
        content.append("You have not saved any rounds yet.")
        content.append(Button("Start a Round", "start_round"))
    else:
        content.append("Your previous rounds:")

        round_options = []

        for i in range(len(state.rounds)):
            golf_round = state.rounds[i]

            content.append(
                "Round " + str(i + 1) +
                " - " + golf_round.course_name +
                ": " + str(golf_round.total_score) +
                " strokes, " +
                describe_score(golf_round.score_to_par)
            )

            round_options.append(str(i))

        average_score = calculate_average_score(state.rounds)

        content.append("Average Score: " + str(round(average_score, 1)))
        content.append("Choose a round to see its details:")
        content.append(
            SelectBox("round_index", round_options, round_options[0])
        )
        content.append(Button("View Selected Round", "round_details"))
        content.append(Button("Start Another Round", "start_round"))

    content.append(Button("Home", "index"))

    return Page(state, content)


# PAGE 6: Details for a selected previous round
@route
def round_details(state: State, round_index: str) -> Page:
    """Display the details of a selected completed round."""
    selected_index = int(round_index)

    if selected_index >= 0 and selected_index < len(state.rounds):
        state.selected_round_index = selected_index
        golf_round = state.rounds[selected_index]

        content = [
            Header("Round Details"),
            "Course: " + golf_round.course_name,
            "Total Strokes: " + str(golf_round.total_score),
            "Total Par: " + str(golf_round.total_par),
            "Result: " + describe_score(golf_round.score_to_par),
            "Individual Hole Scores:"
        ]

        for description in make_hole_descriptions(
                golf_round.scores, golf_round.pars):
            content.append(description)

        content.append(Button("Back to History", "history"))
        content.append(Button("Home", "index"))

        return Page(state, content)

    state.message = "That round could not be found."
    return history(state)


# PAGE 7: Help page
@route
def help(state: State) -> Page:
    """Explain how to use the Golf Score Tracker."""
    return Page(state, [
        Header("How to Use the Golf Score Tracker"),
        "1. Click Start a New Round.",
        "2. Enter your name and the golf course.",
        "3. Enter the number of strokes for each hole.",
        "4. Choose the par for each hole.",
        "5. Click Add Hole to save each hole's score.",
        "6. Click Finish Round when you are done.",
        "7. View your total score and score compared with par.",
        "8. Visit Round History to review previous rounds and your average score.",
        Button("Home", "index"),
        Button("Start a Round", "start_round")
    ])


# UNIT TESTS
def run_tests() -> None:
    """Test calculation helpers and website routes."""
    assert_equal(describe_score(3), "3 over par")
    assert_equal(describe_score(-2), "2 under par")
    assert_equal(describe_score(0), "Even par")

    assert_equal(calculate_totals([5, 4, 6], [4, 4, 5]), (15, 13, 2))
    assert_equal(calculate_totals([3, 3], [4, 5]), (6, 9, -3))

    test_rounds = [
        GolfRound("Course A", [5, 4], [4, 4], 9, 8, 1),
        GolfRound("Course B", [4, 5], [4, 5], 9, 9, 0)
    ]

    assert_equal(calculate_average_score(test_rounds), 9.0)
    assert_equal(calculate_average_score([]), 0.0)

    assert_equal(make_hole_descriptions([5, 4], [4, 3]), [
        "Hole 1: 5 strokes (Par 4)",
        "Hole 2: 4 strokes (Par 3)"
    ])

    test_state = State("", "", [], [], [], -1, "")

    assert_equal(index(test_state).state, test_state)
    assert_equal(start_round(test_state).state, test_state)
    assert_equal(scorecard(test_state).state, test_state)
    assert_equal(history(test_state).state, test_state)
    assert_equal(help(test_state).state, test_state)

    begin_round(test_state, "", "")
    assert_equal(test_state.message,
                 "Please enter both your name and the course name.")

    begin_round(test_state, "Alex", "Test Course")
    assert_equal(test_state.golfer_name, "Alex")
    assert_equal(test_state.course_name, "Test Course")

    add_hole(test_state, 0, "4")
    assert_equal(test_state.current_scores, [])

    add_hole(test_state, 5, "4")
    add_hole(test_state, 4, "4")

    assert_equal(test_state.current_scores, [5, 4])
    assert_equal(test_state.current_pars, [4, 4])

    finish_round(test_state)

    assert_equal(len(test_state.rounds), 1)
    assert_equal(test_state.rounds[0].total_score, 9)
    assert_equal(test_state.rounds[0].total_par, 8)
    assert_equal(test_state.rounds[0].score_to_par, 1)
    assert_equal(test_state.current_scores, [])

    round_summary(test_state)
    round_details(test_state, "0")
    assert_equal(test_state.selected_round_index, 0)

    empty_state = State("", "", [], [], [], -1, "")
    finish_round(empty_state)
    assert_equal(len(empty_state.rounds), 0)

    print("All Golf Score Tracker tests passed!")


# Run tests before starting the website
run_tests()


# Start the website
start_server(State(
    "",
    "",
    [],
    [],
    [],
    -1,
    ""
))

