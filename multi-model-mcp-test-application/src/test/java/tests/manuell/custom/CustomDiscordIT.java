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

public class CustomDiscordIT extends BaseIT {

    static Stream<Arguments> testScenariosProvider() {
        return Stream.of(
                Arguments.of(
                        1,
                        "How many messages does the channel testszenario-1 on the server Benachrichtigungen contain? Answer only with the number of messages.",
                        List.of("get_messages_of_channel")
                ),
                Arguments.of(
                        2,
                        "Create a new thread on the server Benachrichtigungen in the channel allgemein with the question 'How was your day?' and answer it with a positive message.",
                        List.of("create_thread_in_channel")
                ),
                Arguments.of(
                        3,
                        "How many invites are currently pending on the server Benachrichtigungen? Answer only with the number and type of invite.",
                        List.of("get_invites_of_server")
                )
        );
    }

    @ParameterizedTest
    @MethodSource("testScenariosProvider")
    public void testScenarios(int scenarioNumber, String prompt, List<String> tools) throws IOException {
        List<PromptResult> promptResults = Commons.run(prompt, tools);
        CsvWriter.writeToCSV(promptResults, String.format("manuell_stage_%s_discord.csv", OPTIMIZATION_STAGE));
    }
}
