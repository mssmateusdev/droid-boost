from __future__ import annotations

from app.domain.profiles import (
    ActionSnapshotPlan,
    OptimizationAction,
    OptimizationCategory,
    OptimizationProfile,
    ProfileCommand,
)


def animation_scale_action(scale_key: str, value: str, title: str, description: str) -> OptimizationAction:
    return OptimizationAction(
        key=f"{scale_key}_{value}".replace(".", "_"),
        title=title,
        description=description,
        command=ProfileCommand(
            shell=f"settings put global {scale_key} {value}",
            description=f"Set global setting {scale_key} to {value}.",
        ),
        requires_root=False,
        reversible=True,
        snapshot=ActionSnapshotPlan(
            key=f"global.{scale_key}",
            read_shell=f"settings get global {scale_key}",
            restore_shell_template=f"settings put global {scale_key} $value",
            default_restore_shell=f"settings put global {scale_key} 1.0",
        ),
    )


def global_setting_action(
    key: str,
    value: str,
    title: str,
    description: str,
    *,
    default_value: str,
) -> OptimizationAction:
    return OptimizationAction(
        key=f"{key}_{value}".replace(".", "_"),
        title=title,
        description=description,
        command=ProfileCommand(
            shell=f"settings put global {key} {value}",
            description=f"Set global setting {key} to {value}.",
        ),
        requires_root=False,
        reversible=True,
        snapshot=ActionSnapshotPlan(
            key=f"global.{key}",
            read_shell=f"settings get global {key}",
            restore_shell_template=f"settings put global {key} $value",
            default_restore_shell=f"settings put global {key} {default_value}",
        ),
    )


def build_profiles() -> tuple[OptimizationProfile, ...]:
    return (
        OptimizationProfile(
            key="battery_saver",
            title="Battery Saver",
            description="Reduz animacoes e solicita modo de economia de bateria via settings.",
            category=OptimizationCategory.BATTERY,
            actions=(
                animation_scale_action(
                    "window_animation_scale",
                    "0.5",
                    "Reduzir animacao de janelas",
                    "Diminui a escala de animacao de janelas para reduzir trabalho visual.",
                ),
                animation_scale_action(
                    "transition_animation_scale",
                    "0.5",
                    "Reduzir animacao de transicoes",
                    "Diminui transicoes do sistema sem remover funcionalidade.",
                ),
                animation_scale_action(
                    "animator_duration_scale",
                    "0.5",
                    "Reduzir duracao de animadores",
                    "Diminui animadores de UI para respostas mais curtas.",
                ),
                global_setting_action(
                    "low_power",
                    "1",
                    "Solicitar economia de bateria",
                    "Define o setting global low_power como 1 quando o aparelho aceitar.",
                    default_value="0",
                ),
            ),
        ),
        OptimizationProfile(
            key="balanced",
            title="Balanced",
            description="Restaura escalas de animacao padrao e desliga low_power gerenciado.",
            category=OptimizationCategory.BALANCED,
            actions=(
                animation_scale_action(
                    "window_animation_scale",
                    "1.0",
                    "Animacao de janelas padrao",
                    "Restaura a escala de janelas para o comportamento Android padrao.",
                ),
                animation_scale_action(
                    "transition_animation_scale",
                    "1.0",
                    "Transicoes padrao",
                    "Restaura transicoes para a escala Android padrao.",
                ),
                animation_scale_action(
                    "animator_duration_scale",
                    "1.0",
                    "Animadores padrao",
                    "Restaura animadores para a escala Android padrao.",
                ),
                global_setting_action(
                    "low_power",
                    "0",
                    "Desativar low_power gerenciado",
                    "Define o setting global low_power como 0 quando o aparelho aceitar.",
                    default_value="0",
                ),
            ),
        ),
        OptimizationProfile(
            key="responsive",
            title="Responsive",
            description="Torna a UI mais rapida reduzindo animacoes sem desligar tudo.",
            category=OptimizationCategory.RESPONSIVENESS,
            actions=(
                animation_scale_action(
                    "window_animation_scale",
                    "0.25",
                    "Janelas mais responsivas",
                    "Reduz animacoes de janelas para aumentar a sensacao de resposta.",
                ),
                animation_scale_action(
                    "transition_animation_scale",
                    "0.25",
                    "Transicoes mais rapidas",
                    "Reduz transicoes entre telas para diminuir espera visual.",
                ),
                animation_scale_action(
                    "animator_duration_scale",
                    "0.25",
                    "Animadores mais rapidos",
                    "Reduz a duracao de animadores de interface.",
                ),
            ),
        ),
        OptimizationProfile(
            key="gaming",
            title="Gaming",
            description="Minimiza animacoes para reduzir friccao visual antes de jogar.",
            category=OptimizationCategory.GAMING,
            actions=(
                animation_scale_action(
                    "window_animation_scale",
                    "0",
                    "Desativar animacao de janelas",
                    "Remove animacoes de janelas gerenciadas pelo sistema.",
                ),
                animation_scale_action(
                    "transition_animation_scale",
                    "0",
                    "Desativar transicoes",
                    "Remove transicoes visuais entre telas.",
                ),
                animation_scale_action(
                    "animator_duration_scale",
                    "0",
                    "Desativar animadores",
                    "Remove animadores de UI quando o aparelho aceitar.",
                ),
            ),
        ),
    )


PROFILE_PRESETS: tuple[OptimizationProfile, ...] = build_profiles()

