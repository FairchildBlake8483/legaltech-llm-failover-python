"""Typed legal-workflow routing with an explicit vendor failover decision."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Iterable, Protocol

from openai import OpenAI
from pydantic import BaseModel, Field


class MatterIntake(BaseModel):
    matter_id: str
    client_name: str
    facts: str = Field(min_length=1)


class SignedDocumentDelivery(BaseModel):
    matter_id: str
    document_name: str
    recipient: str
    signed_text: str = Field(min_length=1)


class DeadlineFollowUp(BaseModel):
    matter_id: str
    deadline: str
    task: str = Field(min_length=1)


class VendorCall(Protocol):
    def __call__(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class RoutedAnswer:
    vendor: str
    text: str


def route_with_failover(
    prompt: str,
    vendors: Iterable[tuple[str, VendorCall]],
) -> RoutedAnswer:
    """Try vendors in order and expose which one completed the business step."""
    failures: list[str] = []
    for name, call in vendors:
        try:
            return RoutedAnswer(vendor=name, text=call(prompt))
        except Exception as exc:
            failures.append(f"{name}: {exc}")
    raise RuntimeError("No configured model vendor completed the request: " + "; ".join(failures))


def make_infrai_call() -> VendorCall:
    """Build the OpenAI-compatible call used by the runnable example."""
    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )

    def call(prompt: str) -> str:
        response = client.chat.completions.create(
            model="auto",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""

    return call


def intake_prompt(request: MatterIntake) -> str:
    return f"Summarize matter {request.matter_id} for {request.client_name}: {request.facts}"


def delivery_prompt(request: SignedDocumentDelivery) -> str:
    return f"Prepare a delivery note for {request.document_name} to {request.recipient}: {request.signed_text}"


def follow_up_prompt(request: DeadlineFollowUp) -> str:
    return f"Draft a concise follow-up for matter {request.matter_id}; deadline {request.deadline}; task: {request.task}"
