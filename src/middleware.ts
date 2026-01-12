import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const login = process.env.ADMIN_LOGIN;
  const password = process.env.ADMIN_PASSWORD;

  if (!login || !password) {
    return NextResponse.next();
  }

  const authHeader = request.headers.get('authorization');
  if (!authHeader) {
    return unauthorized();
  }

  const [scheme, encoded] = authHeader.split(' ');
  if (scheme !== 'Basic' || !encoded) {
    return unauthorized();
  }

  const decoded = atob(encoded);
  const [user, pass] = decoded.split(':');

  if (user !== login || pass !== password) {
    return unauthorized();
  }

  return NextResponse.next();
}

function unauthorized() {
  return new NextResponse('Unauthorized', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Ozon Margin Dashboard"',
    },
  });
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
