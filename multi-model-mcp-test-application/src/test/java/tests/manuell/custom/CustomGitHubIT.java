package tests.manuell.custom;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import tests.utils.BaseIT;
import tests.utils.Commons;
import tests.utils.CsvWriter;
import tests.utils.PromptResult;

import java.io.IOException;
import java.util.List;
import java.util.stream.Stream;

public class CustomGitHubIT extends BaseIT {

    static Stream<Arguments> testScenariosProvider() {
        return Stream.of(
                Arguments.of(
                        1,
                        "How many open issues does the repo studygroupmap from owner ttomczek have? Answer only with the number. Use only the provided mcp tools.",
                        List.of("get_issues_of_repository")
                ),
                Arguments.of(
                        2,
                        "Create a new issue on the repository studygroupmap by ttomczek. Complain about missing accessibility in a friendly matter. Add a random label. Reply with a link to the Issue.",
                        List.of("create_issue")
                ),
                Arguments.of(
                        3,
                        "How many branch rules does the repository studygroupmap by ttomczek have? Answer only the the number.",
                        List.of("get_infos_about_repo_branches")
                ),
                Arguments.of(
                        4,
                        "Show me a list of all repos i have starred. Only show me the names. My username is ttomczek.",
                        List.of("get_starred_repos_of_user")
                )
        );
    }

    @ParameterizedTest
    @MethodSource("testScenariosProvider")
    public void testScenarios(int scenarioNumber, String prompt, List<String> tools) throws IOException {
        List<PromptResult> promptResults = Commons.run(prompt, tools);
        CsvWriter.writeToCSV(promptResults, String.format("manuell_stage_%s_github.csv", OPTIMIZATION_STAGE));
    }
}
