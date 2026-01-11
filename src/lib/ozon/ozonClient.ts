import pino from 'pino';
import { z } from 'zod';

const logger = pino({ name: 'ozon-client' });

const BASE_URL = 'https://api-seller.ozon.ru';

export type OzonCredentials = {
  clientId: string;
  apiKey: string;
};

export const warehouseListSchema = z.object({
  result: z.array(
    z.object({
      warehouse_id: z.number(),
      name: z.string(),
    }),
  ),
});

async function request<T>(
  path: string,
  credentials: OzonCredentials,
  body: unknown,
  schema: z.ZodSchema<T>,
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  let attempt = 0;
  const maxAttempts = 3;
  let lastError: Error | null = null;

  while (attempt < maxAttempts) {
    attempt += 1;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Client-Id': credentials.clientId,
        'Api-Key': credentials.apiKey,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(body ?? {}),
    });

    const requestId = response.headers.get('x-request-id');

    if (response.ok) {
      const json = await response.json();
      const parsed = schema.safeParse(json);
      if (!parsed.success) {
        logger.error({ issues: parsed.error.issues, requestId }, 'Ozon API schema error');
        throw new Error('Invalid Ozon API response');
      }
      return parsed.data;
    }

    const text = await response.text();
    logger.error({ status: response.status, text, requestId, attempt }, 'Ozon API error');

    if (response.status === 429 || response.status >= 500) {
      const delayMs = 500 * attempt;
      await new Promise((resolve) => setTimeout(resolve, delayMs));
      lastError = new Error(`Ozon API error: ${response.status}`);
      continue;
    }

    throw new Error(`Ozon API error: ${response.status}`);
  }

  throw lastError ?? new Error('Ozon API error');
}

export async function fetchWarehouseList(credentials: OzonCredentials) {
  return request('/v1/warehouse/list', credentials, {}, warehouseListSchema);
}
