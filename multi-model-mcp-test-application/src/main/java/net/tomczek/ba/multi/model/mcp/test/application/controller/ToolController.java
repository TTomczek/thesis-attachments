package net.tomczek.ba.multi.model.mcp.test.application.controller;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.definition.ToolDefinition;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/tools")
public class ToolController {

    private final ToolCallbackProvider toolCallbackProvider;

    public ToolController(ToolCallbackProvider toolCallbackProvider) {
        this.toolCallbackProvider = toolCallbackProvider;
    }

    @GetMapping
    public List<Map<String, String>> getTools() {
        return Arrays.stream(toolCallbackProvider.getToolCallbacks()).map(tool -> {
            ToolDefinition td = tool.getToolDefinition();
            return Map.of(
                "name", td.name(),
                "description", td.description(),
                "inputSchema", td.inputSchema()
            );
        }).collect(Collectors.toList());
    }
}
