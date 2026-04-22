from __future__ import annotations

from app.domain.tweaks import TweakActionKind, TweakCategory, TweakCommand, TweakDefinition, TweakRequirement


CONNECTED = TweakRequirement("Device conectado e autorizado", capability="can_read_diagnostics")
CAN_CHANGE_ANIMATIONS = TweakRequirement(
    "Permissao para alterar animacoes via settings",
    capability="can_change_animations",
)
CAN_CLEAR_CACHE = TweakRequirement(
    "Package manager disponivel para trim de cache",
    capability="can_clear_cache",
)


TWEAK_PRESETS: tuple[TweakDefinition, ...] = (
    TweakDefinition(
        key="animations_off",
        name="Desativar animacoes",
        description="Define as tres escalas globais de animacao como 0 para uma UI mais direta.",
        category=TweakCategory.ANIMATION,
        action_kind=TweakActionKind.SHELL,
        requirements=(CONNECTED, CAN_CHANGE_ANIMATIONS),
        commands=(
            TweakCommand("settings put global window_animation_scale 0", "Janela: 0"),
            TweakCommand("settings put global transition_animation_scale 0", "Transicao: 0"),
            TweakCommand("settings put global animator_duration_scale 0", "Animador: 0"),
        ),
    ),
    TweakDefinition(
        key="animations_fast",
        name="Animacoes rapidas",
        description="Define escalas de animacao como 0.5 para resposta rapida sem remover transicoes.",
        category=TweakCategory.ANIMATION,
        action_kind=TweakActionKind.SHELL,
        requirements=(CONNECTED, CAN_CHANGE_ANIMATIONS),
        commands=(
            TweakCommand("settings put global window_animation_scale 0.5", "Janela: 0.5"),
            TweakCommand("settings put global transition_animation_scale 0.5", "Transicao: 0.5"),
            TweakCommand("settings put global animator_duration_scale 0.5", "Animador: 0.5"),
        ),
    ),
    TweakDefinition(
        key="animations_default",
        name="Restaurar animacoes padrao",
        description="Restaura as tres escalas globais de animacao para 1.0.",
        category=TweakCategory.ANIMATION,
        action_kind=TweakActionKind.SHELL,
        requirements=(CONNECTED, CAN_CHANGE_ANIMATIONS),
        commands=(
            TweakCommand("settings put global window_animation_scale 1.0", "Janela: 1.0"),
            TweakCommand("settings put global transition_animation_scale 1.0", "Transicao: 1.0"),
            TweakCommand("settings put global animator_duration_scale 1.0", "Animador: 1.0"),
        ),
    ),
    TweakDefinition(
        key="open_developer_options",
        name="Abrir opcoes de desenvolvedor",
        description="Abre o menu de opcoes de desenvolvedor no aparelho, quando disponivel.",
        category=TweakCategory.SHORTCUT,
        action_kind=TweakActionKind.SHELL,
        requirements=(CONNECTED,),
        commands=(TweakCommand("am start -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS", "Abrir Developer Options"),),
    ),
    TweakDefinition(
        key="open_battery_settings",
        name="Abrir bateria",
        description="Abre a tela de configuracoes de bateria do Android.",
        category=TweakCategory.SHORTCUT,
        action_kind=TweakActionKind.SHELL,
        requirements=(CONNECTED,),
        commands=(TweakCommand("am start -a android.settings.BATTERY_SETTINGS", "Abrir Battery Settings"),),
    ),
    TweakDefinition(
        key="open_storage_settings",
        name="Abrir armazenamento",
        description="Abre a tela de configuracoes de armazenamento interno.",
        category=TweakCategory.SHORTCUT,
        action_kind=TweakActionKind.SHELL,
        requirements=(CONNECTED,),
        commands=(TweakCommand("am start -a android.settings.INTERNAL_STORAGE_SETTINGS", "Abrir Storage Settings"),),
    ),
    TweakDefinition(
        key="restart_adb",
        name="Reiniciar servidor ADB",
        description="Executa kill-server e start-server para recuperar conexoes instaveis.",
        category=TweakCategory.ADB,
        action_kind=TweakActionKind.ADB,
        requirements=(TweakRequirement("ADB disponivel", requires_device=False),),
        commands=(
            TweakCommand("adb kill-server", "Parar servidor ADB"),
            TweakCommand("adb start-server", "Iniciar servidor ADB"),
        ),
        confirmation_required=True,
    ),
    TweakDefinition(
        key="useful_properties",
        name="Exibir propriedades uteis",
        description="Le getprop e exibe propriedades importantes de produto, build e runtime.",
        category=TweakCategory.DIAGNOSTIC,
        action_kind=TweakActionKind.DIAGNOSTIC_PROPERTIES,
        requirements=(CONNECTED,),
    ),
    TweakDefinition(
        key="memory_storage_state",
        name="Memoria e armazenamento",
        description="Le /proc/meminfo e df /data para um resumo rapido de recursos.",
        category=TweakCategory.DIAGNOSTIC,
        action_kind=TweakActionKind.DIAGNOSTIC_MEMORY_STORAGE,
        requirements=(CONNECTED,),
    ),
    TweakDefinition(
        key="trim_app_cache",
        name="Solicitar limpeza de cache",
        description="Solicita ao package manager trim de caches de apps. Nao remove dados de usuario.",
        category=TweakCategory.STORAGE,
        action_kind=TweakActionKind.SHELL,
        requirements=(CONNECTED, CAN_CLEAR_CACHE),
        commands=(TweakCommand("cmd package trim-caches 999G", "Solicitar trim de caches"),),
        confirmation_required=True,
    ),
)

